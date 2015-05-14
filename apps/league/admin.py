from django.contrib import admin

from apps.league.models import (
    LeagueGame,
    LeagueGroup,
    LeagueBattle,
    LeaguePair,
    LeagueClubInfo,
    LeagueNPCInfo,
)

@admin.register(LeagueGame)
class LeagueGameAdmin(admin.ModelAdmin):
    list_display = ('id', 'current_order', 'create_at')


@admin.register(LeagueGroup)
class LeagueGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'server_id', 'level')


@admin.register(LeagueBattle)
class LeagueBattleAdmin(admin.ModelAdmin):
    list_display = ('id', 'league_group', 'league_order')
    search_fields = ('league_group',)


@admin.register(LeaguePair)
class LeaguePairAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'league_battle', 'club_one', 'club_two',
        'club_one_type', 'club_two_type', 'win_one'
    )
    search_fields = ('league_battle',)


@admin.register(LeagueClubInfo)
class LeagueClubInfoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'club_id', 'group_id', 'battle_times', 'win_times', 'score'
    )

@admin.register(LeagueNPCInfo)
class LeagueNPCInfoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'group_id', 'club_name', 'manager_name', 'staffs',
        'battle_times', 'win_times', 'score',
    )
