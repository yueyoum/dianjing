from django.contrib import admin

from apps.purchase.models import Purchase, Purchase1SDK

@admin.register(Purchase)
class AdminPurchase(admin.ModelAdmin):
    list_display = (
        'id', 'server_id', 'char_id', 'goods_id', 'create_at',
        'platform', 'fee', 'complete_at',
    )

    ordering = ('-create_at',)

@admin.register(Purchase1SDK)
class AdminPurchase1SDK(admin.ModelAdmin):
    list_display = (
        'id', 'ct', 'fee', 'pt', 'sdk', 'ssid',
        'st', 'tcd', 'uid'
    )

    search_fields = ('id', 'tcd',)