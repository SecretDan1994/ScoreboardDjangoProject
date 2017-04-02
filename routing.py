from channels.routing import route, include
from stats.routing import inner_routing as stats_routing

channel_routing = [
    include(stats_routing, path=r'^/gs')
]