from django.contrib import admin
from .models import GameServer, LogTag, ServerLog, Game, Team

from ordered_model.admin import OrderedModelAdmin
# Register your models here.

class GameServerAdmin(OrderedModelAdmin):
    readonly_fields = ('secret_key',)
    ordering = ('order',)

    list_display = ('__str__', 'move_up_down_links')


admin.site.register(GameServer, GameServerAdmin)
admin.site.register(LogTag)
admin.site.register(ServerLog)
admin.site.register(Game)
admin.site.register(Team)
