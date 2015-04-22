from django.contrib import admin

from apps.server.models import Server

@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'status', 'open_at', 'Characters'
    )

    def Characters(self, obj):
        return 0
