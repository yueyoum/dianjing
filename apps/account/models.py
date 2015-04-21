from django.db import models

class BaseAccountManager(models.Manager):
    ACCOUNT_TYPE = None
    def create(self, **kwargs):
        if 'account_id' not in kwargs:
            account = Account.objects.create(tp=self.ACCOUNT_TYPE)
            kwargs['account_id'] = account.id
        return super(BaseAccountManager, self).create(**kwargs)


class AnonymousManager(BaseAccountManager):
    ACCOUNT_TYPE = 'anonymous'

class RegularManager(BaseAccountManager):
    ACCOUNT_TYPE = 'regular'

class ThirdManager(BaseAccountManager):
    ACCOUNT_TYPE = 'third'



class Account(models.Model):
    tp = models.CharField(max_length=32, db_index=True)
    register_at = models.DateTimeField(auto_now_add=True, db_index=True)
    last_login = models.DateTimeField(auto_now=True, db_index=True)

    last_server_id = models.IntegerField(default=0)
    all_server_ids = models.CharField(max_length=255, blank=True)
    login_times = models.IntegerField(default=0)

    class Meta:
        db_table = 'account'

    def save(self, *args, **kwargs):
        if not self.login_times:
            self.login_times = 1
        else:
            self.login_times += 1

        if len(self.all_server_ids) < 255:
            all_server_ids = self.all_server_ids.split(',')
            if self.last_server_id and str(self.last_server_id) not in all_server_ids:
                all_server_ids.append(str(self.last_server_id))

                self.all_server_ids = ','.join(all_server_ids)
                self.all_server_ids = self.all_server_ids[:255]

        super(Account, self).save(*args, **kwargs)



class AccountAnonymous(models.Model):
    account = models.OneToOneField(Account, related_name='info_anonymous')

    objects = AnonymousManager()

    class Meta:
        db_table = 'account_anonymous'


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
