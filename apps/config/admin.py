from django.contrib import admin

from apps.config.models import (
    Config,
    CustomerServiceInformation,
    Bulletin,
    Broadcast,
)

@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('version', 'config', 'des', 'in_use')

@admin.register(CustomerServiceInformation)
class CustomerServiceInformationAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'des')

@admin.register(Bulletin)
class BulletinAdmin(admin.ModelAdmin):
    list_display = ('title', 'content', 'image', 'order_num', 'display')
    ordering = ['-order_num',]
    list_filter = ['display',]

@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ('content', 'repeat_times', 'display')