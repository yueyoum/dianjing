# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       account
Date Created:   2015-09-18 13:28
Description:

"""
import arrow

from django.db.models import F
from django.dispatch import receiver
from core.signals import account_login_signal
from apps.account.models import Account, AccountLoginLog

@receiver(account_login_signal, dispatch_uid='signals.account.account_login_handler')
def account_login_handler(account_id, ip, to_server_id, **kwargs):
    Account.objects.filter(id=account_id).update(
        last_login=arrow.utcnow().format("YYYY-MM-DD HH:mm:ssZ"),
        login_times=F('login_times')+1
    )

    AccountLoginLog.objects.create(
        account_id=account_id,
        ip=ip,
        to_server_id=to_server_id,
    )
