from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import GameServer, LogTag, ServerLog
from contextlib import suppress
from django.db import transaction
from django.utils import timezone
from django.utils.timezone import localtime 
from django.core.cache import cache
import operator

def index(request):
    all_gameservers = GameServer.objects.all()
    context = {
        'all_gameservers':all_gameservers
    }
    return render(request, 'stats/index.html' , context)


@transaction.atomic
def serverstats(request, GameServer_id):
    if GameServer_id:
        gameserver = get_object_or_404(GameServer, id=GameServer_id)
    else:
        raise Http404("GameServer does not exist")

    cached_data = cache.get("stats-scoreboard-gs-{0}".format(GameServer_id))
    if cached_data:
        scoreboard, last_cache_at = cached_data

        for log_entry in gameserver.logs.filter(time__gt=last_cache_at).order_by('-time'):
            scoreboard["logs"].append(log_entry.pretty_print_log)
    else:
        try: 
            custom_round_start = gameserver.logs.filter(tags__name='custom_round_start').order_by('-time')[0]
        except IndexError: 
            raise Http404("Scoreboard for GameServer does not exist")
        scoreboard = custom_round_start.data
        last_cache_at = custom_round_start.time

        scoreboard["logs"] = []
        for log_entry in gameserver.logs.filter(time__gte=last_cache_at).order_by('-time'):
            scoreboard["logs"].append(log_entry.pretty_print_log)

        scoreboard["teams"] = {}
        for team in gameserver.game.teams.all():
            scoreboard["teams"][team.identifier] = team.name

    sub_query = gameserver.logs.filter(time__gt=last_cache_at)
    player_deaths = sub_query.filter(tags__name='player_death')

    for death in player_deaths:
        with suppress(KeyError): # try else for induvidual player
            if scoreboard["players"][death.data["attacker"]] == scoreboard["players"][death.data["steamid"]]:
                with suppress(KeyError):
                    scoreboard["players"][death.data["attacker"]]["kills"] -= 1
                with suppress(KeyError):
                    scoreboard["players"][death.data["steamid"]]["deaths"] += 1
            elif scoreboard["players"][death.data["attacker"]]["team"] == scoreboard["players"][death.data["steamid"]]["team"]:
                with suppress(KeyError):
                    scoreboard["players"][death.data["attacker"]]["kills"] -= 1
                with suppress(KeyError):
                    scoreboard["players"][death.data["steamid"]]["deaths"] += 1
            else:
                with suppress(KeyError):
                    scoreboard["players"][death.data["attacker"]]["kills"] += 1
                with suppress(KeyError):
                    scoreboard["players"][death.data["steamid"]]["deaths"] += 1
        with suppress(KeyError):
            scoreboard["players"][death.data["steamid"]]["alive"] = False


    player_team = sub_query.filter(tags__name='player_team')
    for team in player_team:
        with suppress(KeyError):
            scoreboard["players"][team.data["steamid"]]["team"] = team.data["team"]

    round_end = sub_query.filter(tags__name='round_end')
    for win in round_end:
        with suppress(KeyError):
            scoreboard["teamroundwins"]["{0}".format(win.data["winner"])] += 1

    player_spawn = sub_query.filter(tags__name='player_spawn')
    for spawn in player_spawn:
        with suppress(KeyError):
            scoreboard["players"][spawn.data["steamid"]]["alive"] = True

    player_connect = sub_query.filter(tags__name='player_connect')
    for connect in player_connect:
        with suppress(KeyError):
            scoreboard["players"][connect.data["steamid"]] = {"alive":False, "tag":False, "deaths":0, "kills":0, "ip":connect.data["ip"], "team":4, "name":connect.data["name"]}

#    player_activate = sub_query.filter(tags__name='player_activate')
# add logic to only add when activate backkquerying player_connect for more info
    
    round_mvp = sub_query.filter(tags__name='round_mvp')
    for mvp in round_mvp:
        with suppress(KeyError):
            scoreboard["players"][mvp.data["steamid"]]["mvp"] += 1

    player_disconnect = sub_query.filter(tags__name='player_disconnect')
    for disconnect in player_disconnect:
        with suppress(KeyError):    
            del scoreboard["players"][disconnect.data["steamid"]]

    player_changename = sub_query.filter(tags__name='player_changename')
    for namechange in player_changename:
        with suppress(KeyError):
            scoreboard["players"][namechange.data["steamid"]]["name"] = namechange.data["newname"]

    #Variables

    round_count = scoreboard["teamroundwins"]["2"] + scoreboard["teamroundwins"]["3"] + 1
    player_count = 0
    for players in scoreboard["players"]:
        player_count += 1

    ct_player_count = 0
    t_player_count = 0
    spec_player_count = 0
    ct_alive_count = 0
    t_alive_count = 0

    steamid_with_kills_list = []
    sorted_steamid_list = []

    for steamid, data in scoreboard["players"].items():
        steamid_with_kills_list.append((steamid, data["kills"]))

    sorted_steamid_with_kills_list = sorted(steamid_with_kills_list, key=operator.itemgetter(1), reverse = True)

    for x in sorted_steamid_with_kills_list:
        sorted_steamid_list.append(x[0])

    for steamid, data in scoreboard["players"].items():
        if data["team"] == 3 and data["alive"] == True:
            ct_player_count += 1
            ct_alive_count += 1
        elif data["team"] == 2 and data["alive"] == True:
            t_player_count += 1
            t_alive_count += 1
        elif data["team"] == 3 and data["alive"] == False:
            ct_player_count += 1
        elif data["team"] == 2 and data["alive"] == False:
            t_player_count += 1
        else:
            spec_player_count += 1

    ct_round_wins = scoreboard["teamroundwins"]["3"]
    t_round_wins = scoreboard["teamroundwins"]["2"]

    #at end calc kdr
    for player in scoreboard["players"].keys():
        try:
            with suppress(KeyError):
                kd = scoreboard["players"][player]["kills"]/scoreboard["players"][player]["deaths"]
        except ZeroDivisionError:
            kd = scoreboard["players"][player]["kills"]

        scoreboard["players"][player]["kd"] = '{0:.2f}'.format(kd)

    generation_time = gameserver.logs.all().order_by('-time')[0].time
    cache.set("stats-scoreboard-gs-{0}".format(GameServer_id), (scoreboard, generation_time))

    context = {
        'scoreboard':scoreboard,
        'scoreboard_gen_time':generation_time,
        'specteams':(1,4),
        'round_count':round_count,
        'player_count':player_count,
        'ct_player_count':ct_player_count,
        't_player_count':t_player_count,
        'spec_player_count':spec_player_count,
        'ct_alive_count':ct_alive_count,
        't_alive_count':t_alive_count,
        'sorted_list':sorted_steamid_list,
        'ct_round_wins':ct_round_wins,
        't_round_wins':t_round_wins,
    }
    return render(request, 'stats/serverstats.html' , context)