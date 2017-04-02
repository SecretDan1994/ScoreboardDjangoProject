from django.conf.urls import include
from django.conf.urls import url
from . import views

urlpatterns = [

    # /servers/
    url(r'^$', views.index, name='index'),
	
    # /servers/1/stats
    url(r'^(?P<GameServer_id>[0-9]+)/stats$', views.serverstats, name='serverstats'),
]