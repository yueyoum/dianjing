# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.config.models import (
    Config,
    CustomerServiceInformation,
    Bulletin,
    Broadcast,
    Mail,
)

@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ('version', 'config', 'client_config', 'des', 'in_use')

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
    list_display = ('server_min', 'server_max', 'content', 'repeat_times')

@admin.register(Mail)
class AdminMail(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'send_at',
        'condition_type', 'condition_value',
        'create_at', 'status'
    )

    fieldsets = (
        (None, {
            'fields': (
                'title', 'content', 'items', 'send_at',
                'condition_type', 'condition_value',
            )
        }),

        ('条件', {
            'classes': ('collapse', ),
            'fields': (
                'condition_club_level', 'condition_vip_level',
                'condition_login_at_1', 'condition_login_at_2',
                'condition_exclude_chars',
            )
        })
    )

    list_filter = ('status',)
    actions = ['action_make_status_waiting',]

    def action_make_status_waiting(self, request, queryset):
        queryset.update(status=0)
    action_make_status_waiting.short_description = u'重置为等待发送状态'
