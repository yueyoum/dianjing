from django.contrib import admin

from apps.league.models import (
    LeagueGame,
    LeagueGroup,
    LeagueBattle,
    LeagueClubInfo,
    LeagueNPCInfo,
)

@admin.register(LeagueGame)
class LeagueGameAdmin(admin.ModelAdmin):
    list_display = ('id', 'current_order', 'create_at')


@admin.register(LeagueGroup)
class LeagueGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'level')


@admin.register(LeagueBattle)
class LeagueBattleAdmin(admin.ModelAdmin):
    list_display = ('id', 'league_group', 'league_order', 'club_one', 'club_two', 'npc_one', 'npc_two')


@admin.register(LeagueClubInfo)
class LeagueClubInfoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'club_id', 'group_id', 'battle_times', 'score'
    )

@admin.register(LeagueNPCInfo)
class LeagueNPCInfoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'club_name', 'manager_name', 'npc_id', 'staffs_info'
    )
