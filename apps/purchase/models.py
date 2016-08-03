# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models

class Purchase(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    server_id = models.IntegerField(db_index=True)
    char_id = models.IntegerField(db_index=True)

    # 1001 是月卡
    goods_id = models.IntegerField()
    goods_amount = models.IntegerField()

    create_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # 上面是 prepare 的时候就记录下来的
    # 下面是平台回调时记录的信息

    # 金额，分
    fee = models.IntegerField(default=0)

    channel_id = models.CharField(db_index=True, max_length=255, blank=True)
    ssid = models.CharField(max_length=255, blank=True)

    # tcd 订单号， 唯一。
    # 这里没用unique 是因为 用户支付前，要先到自己服务器上 prepare 一下
    # 这时候就会创建 Purchase 记录。 而此时 tcd 是没有的
    unique_trade_id = models.CharField(db_index=True, max_length=255, blank=True)
    return_code = models.IntegerField(default=0)

    # 最后需要更新这个 0 表示没有完成 UTC秒
    complete_timestamp = models.IntegerField(default=0, db_index=True)

    class Meta:
        db_table = 'purchase'
        verbose_name = '充值'
        verbose_name_plural = '充值'
