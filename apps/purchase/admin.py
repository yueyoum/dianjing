import arrow

from django.conf import settings
from django.contrib import admin

from apps.purchase.models import Purchase

@admin.register(Purchase)
class AdminPurchase(admin.ModelAdmin):
    list_display = (
        'id', 'server_id', 'char_id', 'goods_id', 'create_at',
        'fee', 'channel_id', 'ssid', 'unique_trade_id', 'return_code',
        'complete_timestamp',
        'complete_timestamp_parsed',
    )

    def complete_timestamp_parsed(self, obj):
        if not obj.complete_timestamp:
            return 0

        date = arrow.get(obj.complete_timestamp).to(settings.TIME_ZONE)
        return date.format("YYYY-MM-DD HH:mm:ss")

    ordering = ('create_at',)