# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       core
Date Created:   2015-04-22 14:25
Description:

"""

from django.db import transaction, IntegrityError

from dianjing.exception import GameException
from apps.account.models import AccountRegular

def register(name, password):
    try:
        with transaction.atomic():
            account = AccountRegular.objects.create(name=name, passwd=password)
    except IntegrityError:
        raise GameException(1)

    return account


def regular_login(name, password):
    try:
        account = AccountRegular.objects.select_related('account').get(name=name)
    except AccountRegular.DoesNotExist:
        raise GameException(1)

    if account.passwd != password:
        raise GameException(1)

    return account


def third_login(platform, uid, param):
    raise NotImplementedError()


