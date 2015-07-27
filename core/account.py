# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       account
Date Created:   2015-07-01 15:35
Description:

"""


from django.db import transaction, IntegrityError

from dianjing.exception import GameException
from apps.account.models import AccountRegular
from config import ConfigErrorMessage

def register(name, password):
    if not name or not password:
        raise GameException( ConfigErrorMessage.get_error_id("BAD_MESSAGE") )
    try:
        with transaction.atomic():
            account = AccountRegular.objects.create(name=name, passwd=password)
    except IntegrityError:
        raise GameException( ConfigErrorMessage.get_error_id("ACCOUNT_NAME_TAKEN") )

    return account


def regular_login(name, password):
    if not name or not password:
        raise GameException( ConfigErrorMessage.get_error_id("BAD_MESSAGE") )

    try:
        account = AccountRegular.objects.select_related('account').get(name=name)
    except AccountRegular.DoesNotExist:
        raise GameException( ConfigErrorMessage.get_error_id("ACCOUNT_CANNOT_FIND_NAME") )

    if account.passwd != password:
        raise GameException( ConfigErrorMessage.get_error_id("ACCOUNT_WRONG_PASSWORD") )

    return account


def third_login(platform, uid, param):
    raise NotImplementedError()

