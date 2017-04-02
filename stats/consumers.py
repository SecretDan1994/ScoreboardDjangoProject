from django.utils import timezone
from django.db import transaction

from channels import Channel, Group
from channels.sessions import channel_session

from django.core.exceptions import ObjectDoesNotExist

import json


from .models import GameServer, LogTag, ServerLog

MY_SECRET_KEY = '14bf64cd-fd78-40e8-b42a-c351c0f5ff9d'

# Connected to websocket.connect
# @enforce_ordering(slight=False)
@channel_session
def ws_connect(message, **kwargs):
	print("ws_connect - OK")
	try:
		secret_key = kwargs["secret-key"]
		remote_ip = message.content['client'][0] # https://github.com/django/channels/issues/385
	except KeyError:
		# Unauthorised
		message.reply_channel.send({"close": True})
		return
	else:
		try:
			gameserver = GameServer.objects.get(secret_key=secret_key, ip=remote_ip)
		except ObjectDoesNotExist: # Unauthorised
			# Unauthorised
			message.reply_channel.send({"close": True})
			return
		else:
			# authorised
			message.reply_channel.send({"accept": True})
			message.reply_channel.send({"secret-key": MY_SECRET_KEY})
			message.channel_session['gs_id'] = gameserver.id
	

# Connected to websocket.receive
# @enforce_ordering(slight=False)
@channel_session
def ws_receive(message):
	message.content['text']
	print("ws_receive - OK")


# Connected to websocket.disconnect
# @enforce_ordering(slight=False)
@channel_session
def ws_disconnect(message):
	print("ws_disconnect - OK")