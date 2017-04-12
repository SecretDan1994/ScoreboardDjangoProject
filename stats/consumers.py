from django.utils import timezone
from django.db import transaction

from channels import Channel, Group
from channels.sessions import channel_session, enforce_ordering

from django.core.exceptions import ObjectDoesNotExist

import json

from .models import GameServer, LogTag, ServerLog
from .tasks import on_recieve_stats_msg

MY_SECRET_KEY = '14bf64cd-fd78-40e8-b42a-c351c0f5ff9d'

# Connected to websocket.connect
# @enforce_ordering(slight=False)
@enforce_ordering
@channel_session
def ws_connect(message, **kwargs):
	print("ws_connect - OK")
	try:
		secret_key = kwargs["secretkey"]
#		headers = {x[0].decode():x[1].decode() for x in message.content["headers"]}

#		if headers['x-real-ip'] == headers['x-forwarded-for']:
#			remote_ip = headers['x-forwarded-for']
#		else:
#			raise NotImplementedError #proxy was used

#		remote_ip = message.content['client'][0] # https://github.com/django/channels/issues/385

# IP checking does not work with NFO, random multiple ips

	except (KeyError, NotImplementedError):
		# Unauthorised
		message.reply_channel.send({"close": True})
		print("ws_connect - NO AUTH : BAD FORMAT")
		return
	else:
		try:
			gameserver = GameServer.objects.get(secret_key=secret_key) # auth by ip too~:  ip=remote_ip
		except ObjectDoesNotExist: # Unauthorised
			# Unauthorised
			print("ws_connect - unauthorised", secret_key) #remote_ip)
			message.reply_channel.send({"close": True})
			return
		else:
			# authorised
			gameserver.connected = True
			gameserver.save()
			message.channel_session['gs_id'] = gameserver.id
			message.reply_channel.send({"accept": True}) # , immediately=True
			Group("server-%s" % message.channel_session['gs_id']).add(message.reply_channel)
			print("ws_connect - authorised", secret_key, message.channel_session['gs_id']) #remote_ip)
#			message.reply_channel.send({"secret-key": MY_SECRET_KEY}) # ensure ordering for this
			

# Connected to websocket.receive
# @enforce_ordering(slight=False)
@enforce_ordering
@channel_session
def ws_receive(message):
#	message.content['text'] = ""
#	message.reply_channel.send({"text": "",})
	print("ws_receive - OK")
	try:
		msg = json.loads(message.content['text'])
		msg_cmd = msg["cmd"]
	except Exception as e:
		print("ws_receive", e)
	else:
		print("ws_receive - calling func", msg_cmd)
		if msg_cmd == "gs-stats":
			# celery delay this func call
#			on_recieve_stats_msg(msg["kwargs"], msg["id"], message.channel_session['gs_id'], message.content)
			on_recieve_stats_msg.apply_async((msg["kwargs"], msg["id"], message.channel_session['gs_id'], message.content,),)

			Group("server-%s" % message.channel_session['gs_id']).send({
					"text": msg,
				})

# Connected to websocket.disconnect
# @enforce_ordering(slight=False)
@enforce_ordering
@channel_session
def ws_disconnect(message):
	print("ws_disconnect - OK")
	try:
		gameserver = GameServer.objects.get(id = message.channel_session['gs_id'])
	except KeyError:
		print("ws_disconnect - KeyError")
	except ObjectDoesNotExist:
		print("ws_disconnect - ObjDN")
	else:
		gameserver.connected = False
		gameserver.save()
		Group("server-%s" % message.channel_session['gs_id']).discard(message.reply_channel)