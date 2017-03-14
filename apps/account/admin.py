# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.account.models import (
    Account, AccountLoginLog,
    AccountRegular,
    GeTuiClientID,
)

from utils.session import LoginID

def make_account_relogin(modeladmin, request, queryset):
    for q in queryset:
        LoginID.delete(q.id)
make_account_relogin.short_description = u"强制重登陆"


@admin.register(AccountRegular)
class AdminAccountRegular(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'passwd'
    )

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'tp', 'Name', 'Password', 'Provider', 'Platform',
        'register_at', 'last_login', 'login_times',
    )

    readonly_fields = (
        'tp', 'register_at', 'last_login', 'login_times',
    )

    actions = [make_account_relogin,]

    def Name(self, obj):
        if obj.tp == 'regular':
            return obj.info_regular.name
        return ''

    def Password(self, obj):
        if obj.tp == 'regular':
            return obj.info_regular.passwd
        return ''

    def Provider(self, obj):
        if obj.tp == 'third':
            return obj.info_third.provider
        return ''

    def Platform(self, obj):
        if obj.tp == 'third':
            return obj.info_third.platform
        return ''

    # def Puid(self, obj):
    #     if obj.tp == 'third':
    #         return obj.info_third.uid
    #     return ''

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AccountLoginLog)
class AccountLoginLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_id', 'login_at', 'ip', 'to_server_id')
    search_fields = ('account_id',)


@admin.register(GeTuiClientID)
class AdminGeTuiClientID(admin.ModelAdmin):
    list_display = ('id', 'client_id')
    search_fields = ('id',)
    readonly_fields = ('id', 'client_id')
