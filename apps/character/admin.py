from django.contrib import admin

from apps.character.models import Character

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'account_id', 'server_id', 'name', 'create_at',
        'club_name',
    )

    search_fields = ['name',]
