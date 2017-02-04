from django.contrib import admin

from apps.gift_code.models import GiftCode, GiftCodeGen, GiftCodeUsingLog

@admin.register(GiftCode)
class AdminGiftCode(admin.ModelAdmin):
    list_display = (
        'id', 'items',
        'mail_title', 'mail_content',
        'times_limit',
        'active', 'create_at',
        'time_range1', 'time_range2',
    )

@admin.register(GiftCodeGen)
class AdminGiftCodeGen(admin.ModelAdmin):
    list_display = (
        'category', 'amount', 'used_amount', 'create_at',
        'Download'
    )

    def Download(self, obj):
        return '<a href="/gift_code/download?gen_id={0}" target="_blank">Download</a>'.format(obj.id)
    Download.allow_tags = True


@admin.register(GiftCodeUsingLog)
class AdminGiftCodeUsingLog(admin.ModelAdmin):
    list_display = (
        'id', 'server_id', 'char_id', 'gift_code', 'category', 'using_at'
    )

    ordering = ('-using_at', )

    readonly_fields = list_display