# -*- coding: utf-8 -*-


from django.db import models


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

    login_times = models.IntegerField(default=0)

    class Meta:
        db_table = 'account'

    def save(self, *args, **kwargs):
        if not self.login_times:
            self.login_times = 1
        else:
            self.login_times += 1

        super(Account, self).save(*args, **kwargs)


class AccountRegular(models.Model):
    name = models.CharField(unique=True, max_length=255)
    passwd = models.CharField(max_length=255)
    account = models.OneToOneField(Account, related_name='info_regular')

    objects = RegularManager()

    class Meta:
        db_table = 'account_regular'


class AccountThird(models.Model):
    platform = models.CharField(max_length=255)
    uid = models.CharField(max_length=255)
    account = models.OneToOneField(Account, related_name='info_third')

    objects = ThirdManager()

    class Meta:
        db_table = 'account_third'
        unique_together = (('platform', 'uid'),)


class AccountLoginLog(models.Model):
    account_id = models.IntegerField(db_index=True, verbose_name="帐号ID")
    login_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="登录时间")
    ip = models.CharField(max_length=32, verbose_name="登录IP")
    to_server_id = models.IntegerField(verbose_name="区ID")

    class Meta:
        db_table = 'account_login_log'
        verbose_name = "登录日志"
        verbose_name_plural = "登录日志"


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
