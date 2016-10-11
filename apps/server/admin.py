from django.contrib import admin

from apps.server.models import Server
from apps.character.models import Character

@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'status', 'open_at', 'Characters',
    )

    def Characters(self, obj):
        return Character.objects.filter(server_id=obj.id).count()
