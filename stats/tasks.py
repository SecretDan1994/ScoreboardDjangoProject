from __future__ import absolute_import

from datetime import datetime
from django.utils.timezone import utc

from celery import shared_task
from .models import GameServer, LogTag
from django.core.cache import cache

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
	
	gameserver.logs.create(time=time, data=data, kind="gs-stats", tag=tag)

	print("TASK OK - on_recieve_stats_msg")
	if kind == "snapshot":
		cache.delete("stats-scoreboard-gs-{0}".format(gameserver.id))

