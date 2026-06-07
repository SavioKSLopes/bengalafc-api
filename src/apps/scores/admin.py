from django.contrib import admin
from .models import FantasyLineup, FantasyLineupPlayer, FantasyTransfer, Player, ScoreEvent


class FantasyLineupPlayerInline(admin.TabularInline):
    model = FantasyLineupPlayer
    extra = 0


@admin.register(FantasyLineup)
class FantasyLineupAdmin(admin.ModelAdmin):
    list_display = ('user', 'stage', 'captain', 'updated_at')
    list_filter = ('stage',)
    search_fields = ('user__username', 'captain__name')
    inlines = (FantasyLineupPlayerInline,)


@admin.register(FantasyTransfer)
class FantasyTransferAdmin(admin.ModelAdmin):
    list_display = ('user', 'stage', 'from_player', 'to_player', 'created_at')
    list_filter = ('stage',)
    search_fields = ('user__username', 'from_player__name', 'to_player__name')


admin.site.register(Player)
admin.site.register(ScoreEvent)
