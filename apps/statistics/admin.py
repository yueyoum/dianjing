from django.contrib import admin

from apps.statistics.models import Statistics

@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'create_at',
        'server_id', 'char_id',
        'club_gold', 'club_diamond',
        'message'
    )

    search_fields = ['char_id',]
