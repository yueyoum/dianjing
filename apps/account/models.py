from django.db import models

class BaseAccountManager(models.Manager):
    ACCOUNT_TYPE = None
    def create(self, **kwargs):
        if 'account_id' not in kwargs:
            account = Account.objects.create(tp=self.ACCOUNT_TYPE)
            kwargs['account_id'] = account.id
        return super(BaseAccountManager, self).create(**kwargs)


class RegularManager(BaseAccountManager):
    ACCOUNT_TYPE = 'regular'

class ThirdManager(BaseAccountManager):
    ACCOUNT_TYPE = 'third'


class Account(models.Model):
    tp = models.CharField(max_length=32, db_index=True)
    register_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_login = models.DateTimeField(auto_now=True, db_index=True)

    last_server_id = models.IntegerField(default=0)
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
