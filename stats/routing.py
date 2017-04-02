from channels.routing import route
from . import consumers

inner_routing = [
	route("websocket.connect", consumers.ws_connect, path=r"^/(?P<secret-key>[-\w]+)/$"),
	route("websocket.receive", consumers.ws_receive),
	route("websocket.disconnect", consumers.ws_disconnect),
]
