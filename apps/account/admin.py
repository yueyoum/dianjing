from django.contrib import admin

from apps.account.models import (
    Account,
)



@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'tp', 'Name', 'Password', 'Token', 'Platform', 'Puid',
        'register_at', 'last_login', 'last_server_id', 'all_server_ids',
        'login_times',
    )

    readonly_fields = (
        'tp', 'last_server_id', 'all_server_ids', 'login_times'
    )

    ordering = ('-last_login',)

    def Name(self, obj):
        if obj.tp == 'regular':
            return obj.info_regular.name
        return ''

    def Password(self, obj):
        if obj.tp == 'regular':
            return obj.info_regular.passwd
        return ''

    def Token(self, obj):
        if obj.tp == 'anonymous':
            return obj.info_anonymous.id
        return ''

    def Platform(self, obj):
        if obj.tp == 'third':
            return obj.info_third.platform
        return ''

    def Puid(self, obj):
        if obj.tp == 'third':
            return obj.info_third.uid
        return ''

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
