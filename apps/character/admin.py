# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.character.models import Character, ForbidChat


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'account_id', 'server_id', 'name', 'create_at',
        'last_login', 'login_times',
    )

    readonly_fields = (
        'account_id', 'server_id', 'name', 'login_times'
    )

    search_fields = ['name', ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ForbidChat)
class AdminForbidChat(admin.ModelAdmin):
    list_display = ('id', 'char_id', 'create_at', 'unforbidden_at', 'reason')

    search_fields = ('char_id',)
