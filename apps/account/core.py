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
from config import CONFIG

def register(name, password):
    if not name or not password:
        raise GameException( CONFIG.ERRORMSG["BAD_MESSAGE"].id )
    try:
        with transaction.atomic():
            account = AccountRegular.objects.create(name=name, passwd=password)
    except IntegrityError:
        raise GameException( CONFIG.ERRORMSG["ACCOUNT_NAME_TAKEN"].id )

    return account


def regular_login(name, password):
    if not name or not password:
        raise GameException( CONFIG.ERRORMSG["BAD_MESSAGE"].id )

    try:
        account = AccountRegular.objects.select_related('account').get(name=name)
    except AccountRegular.DoesNotExist:
        raise GameException( CONFIG.ERRORMSG["ACCOUNT_CANNOT_FIND_NAME"].id )

    if account.passwd != password:
        raise GameException( CONFIG.ERRORMSG["ACCOUNT_WRONG_PASSWORD"].id )

    return account


def third_login(platform, uid, param):
    raise NotImplementedError()


