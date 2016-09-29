# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models

class Purchase(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    server_id = models.IntegerField(db_index=True)
    char_id = models.IntegerField(db_index=True)

    # 1001 是月卡
    goods_id = models.IntegerField()

    create_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # 平台 1sdk, ios ...
    platform = models.CharField(max_length=255)

    # 金额， 分
    fee = models.IntegerField(default=0)
    # 是否客户端来确认过
    verified = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = 'purchase'
        verbose_name = '充值'
        verbose_name_plural = '充值'


class Purchase1SDK(models.Model):
    # 这个id 就是 Purchase 中的id
    id = models.CharField(primary_key=True, max_length=255)
    ct = models.IntegerField(db_index=True)
    fee = models.IntegerField()
    pt = models.IntegerField()
    sdk = models.CharField(max_length=255, db_index=True)
    ssid = models.CharField(max_length=255)
    st = models.IntegerField()
    # 平台唯一订单号
    tcd = models.CharField(max_length=255, unique=True)
    uid = models.CharField(max_length=255)

    class Meta:
        db_table = 'purchase_1sdk'
        verbose_name = '充值-1sdk'
        verbose_name_plural = '充值-1sdk'