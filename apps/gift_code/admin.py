from django.contrib import admin

from apps.gift_code.models import GiftCode, GiftCodeUsingLog

@admin.register(GiftCode)
class AdminGiftCode(admin.ModelAdmin):
    list_display = (
        'id', 'items',
        'mail_title', 'mail_content',
        'times_limit',
        'active', 'create_at',
        'time_range1', 'time_range2',
    )

@admin.register(GiftCodeUsingLog)
class AdminGiftCodeUsingLog(admin.ModelAdmin):
    list_display = (
        'id', 'char_id', 'gift_code', 'using_at'
    )

    ordering = ('-using_at', )

    readonly_fields = list_display
