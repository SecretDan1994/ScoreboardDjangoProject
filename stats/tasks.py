from __future__ import absolute_import

from datetime import datetime
from django.utils.timezone import utc

from celery import shared_task
from .models import GameServer, LogTag
from django.core.cache import cache
from channels import Channel, Group
from channels.sessions import channel_session
import json

import pytz

#todo ensure tags exist on connect
# render scoreboard on snapshot instead of only deleting it?
@shared_task
def on_recieve_stats_msg(msg, msg_id, gs_id, reply_channel):
	print("Task RECV - on_recieve_stats_msg")
	time = datetime.fromtimestamp(msg["time"]).replace(tzinfo=pytz.UTC)
#	now = datetime.datetime.utcnow().replace(tzinfo=utc)

	kind = msg["kind"]
	data = msg["data"]

	gameserver = GameServer.objects.get(id = gs_id)
	tag = LogTag.objects.get(name=kind)
	
	log = gameserver.logs.create(time=time, data=data, kind="gs-stats", tag=tag)

	print("TASK OK - on_recieve_stats_msg")
	if kind == "snapshot":
		cache.delete("stats-scoreboard-gs-{0}".format(gameserver.id))

	Group("scoreboard-live-{0}".format(gs_id)).send({
	 						"text": json.dumps({
	 							"cmd":"gs-stats-liveupdate", 
	 							"payload": {
	 								"time": time.isoformat(),
	 								"data": data,
	 								"tag": tag.name,
	 								"dbid": tag.id,
	 								"pretty_print": log.pretty_print_log,
	 							}
	 						}),
	})

