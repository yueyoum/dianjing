# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       purchase
Date Created:   2015-09-17 17:33
Description:

"""

from django.dispatch import receiver

from core.signals import purchase_done_signal
from core.purchase import Purchase
from core.activity import ActivityPurchaseDaily, ActivityPurchaseContinues


@receiver(purchase_done_signal, dispatch_uid='signals.purchase.purchase_done_handler')
def purchase_done_handler(server_id, char_id, goods_id, got, actual_got, **kwargs):
    info = Purchase(server_id, char_id).get_purchase_info_of_day_shift()
    if len(info) == 1:
        # 今天第一次充值
        ActivityPurchaseDaily(server_id, char_id).add_count()
        ActivityPurchaseContinues(server_id, char_id).record()
