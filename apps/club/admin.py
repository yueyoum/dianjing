from django.contrib import admin

from apps.club.models import Club

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'char_id', 'char_name', 'server_id',
        'name', 'flag', 'level', 'renown', 'vip',
        'exp', 'gold', 'sycee'
    )
