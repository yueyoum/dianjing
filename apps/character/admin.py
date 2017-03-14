# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.character.models import Character, ForbidChat
from utils.session import LoginID

def make_char_relogin(modeladmin, request, queryset):
    for q in queryset:
        LoginID.delete(q.account_id)
make_char_relogin.short_description = u"强制重登陆"

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
    actions = [make_char_relogin,]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ForbidChat)
class AdminForbidChat(admin.ModelAdmin):
    list_display = ('id', 'char_id', 'create_at', 'unforbidden_at', 'reason')

    search_fields = ('char_id',)
