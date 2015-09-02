from django.contrib import admin

from apps.config.models import Config

@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('version', 'config', 'des', 'in_use')
