# -*- coding: utf-8 -*-

import uuid
import arrow

from django.db import models
from django.db import connection


class BaseAccountManager(models.Manager):
    ACCOUNT_TYPE = None

    def create(self, **kwargs):
        if 'account_id' not in kwargs:
            account = Account.objects.create(tp=self.ACCOUNT_TYPE)
            kwargs['account_id'] = account.id
        return models.Manager.create(self, **kwargs)


class RegularManager(BaseAccountManager):
    ACCOUNT_TYPE = 'regular'


class ThirdManager(BaseAccountManager):
    ACCOUNT_TYPE = 'third'


class Account(models.Model):
    tp = models.CharField(max_length=32, db_index=True)
    register_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_login = models.DateTimeField(auto_now=True, db_index=True)

    login_times = models.BigIntegerField(default=0)

    class Meta:
        db_table = 'account'
        ordering = ['-last_login', ]
        verbose_name = '帐号'
        verbose_name_plural = '帐号'


class AccountRegular(models.Model):
    name = models.CharField(unique=True, max_length=255)
    passwd = models.CharField(max_length=255)
    account = models.OneToOneField(Account, related_name='info_regular')

    objects = RegularManager()

    class Meta:
        db_table = 'account_regular'


class AccountThird(models.Model):
    provider = models.CharField(max_length=255) # 集成接入供应商，比如1sdk 这些
    platform = models.CharField(max_length=255) # 各种渠道，小米，360 这些
    uid = models.CharField(max_length=255) # 用户在渠道上的唯一id
    account = models.OneToOneField(Account, related_name='info_third')

    objects = ThirdManager()

    class Meta:
        db_table = 'account_third'
        unique_together = (('provider', 'platform', 'uid'),)


class AccountLoginLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    account_id = models.IntegerField(db_index=True, verbose_name="帐号ID")
    login_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="登录时间")
    ip = models.CharField(max_length=32, verbose_name="登录IP")
    to_server_id = models.IntegerField(verbose_name="区ID")

    class Meta:
        db_table = 'account_login_log'
        ordering = ['-login_at', ]
        verbose_name = "登录日志"
        verbose_name_plural = "登录日志"

    @classmethod
    def cronjob(cls):
        connection.close()

        limit = arrow.utcnow().replace(days=-60).format("YYYY-MM-DD HH:mm:ssZ")
        cls.objects.filter(login_at__lte=limit).delete()

    @classmethod
    def get_recent_login_account_ids(cls, recent_days):
        from utils.functional import get_start_time_of_today

        assert recent_days > 0
        recent_days -= 1

        limit = get_start_time_of_today()
        limit = limit.replace(days=-recent_days)
        account_ids = {}

        for log in cls.objects.filter(login_at__gte=limit.format("YYYY-MM-DD HH:mm:ssZ")).order_by('login_at'):
            account_ids[log.account_id] = log.to_server_id

        return account_ids

class AccountBan(models.Model):
    account_id = models.IntegerField(verbose_name="帐号ID")
    ban = models.BooleanField(verbose_name="是否冻结")

    ban_at = models.DateTimeField(auto_now_add=True, verbose_name="冻结开始时间")
    unban_at = models.DateTimeField(db_index=True, verbose_name="冻结结束时间")
    reason = models.TextField(blank=True, verbose_name="原因")

    class Meta:
        db_table = 'account_ban'
        unique_together = (('account_id', 'ban'),)

        verbose_name = "帐号冻结"
        verbose_name_plural = "账号冻结"


class GeTuiClientID(models.Model):
    id = models.IntegerField(primary_key=True)  # 就是 account id
    client_id = models.CharField(max_length=255)

    class Meta:
        db_table = 'getui_clientid'
        verbose_name = "个推clientid"
        verbose_name_plural = "个推clientid"
