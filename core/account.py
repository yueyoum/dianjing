# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       account
Date Created:   2015-07-01 15:35
Description:

"""

import requests

from django.db import transaction, IntegrityError
from django.db.models import Q

from dianjing.exception import GameException
from apps.account.models import AccountRegular, AccountThird
from config import ConfigErrorMessage


def register(name, password):
    if not name or not password:
        raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))
    try:
        with transaction.atomic():
            account = AccountRegular.objects.create(name=name, passwd=password)
    except IntegrityError:
        raise GameException(ConfigErrorMessage.get_error_id("ACCOUNT_NAME_TAKEN"))

    return account


def regular_login(name, password):
    if not name or not password:
        raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

    try:
        account = AccountRegular.objects.select_related('account').get(name=name)
    except AccountRegular.DoesNotExist:
        raise GameException(ConfigErrorMessage.get_error_id("ACCOUNT_CANNOT_FIND_NAME"))

    if account.passwd != password:
        raise GameException(ConfigErrorMessage.get_error_id("ACCOUNT_WRONG_PASSWORD"))

    return account


def third_login(platform, uid, param):
    if not platform or not uid or not param:
        raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

    # verify
    url = "http://sync.1sdk.cn/login/check.html"
    params = {
        'sdk': platform,
        'app': '{E15E4E08-795DB177}',
        'uin': uid,
        'sess': param
    }

    req = requests.get(url, params=params)
    print req.content

    if not req.ok or req.content != '0':
        raise GameException(ConfigErrorMessage.get_error_id("ACCOUNT_LOGIN_FAILURE"))

    try:
        condition = Q(platform=platform) & Q(uid=uid)
        account = AccountThird.objects.select_related('account').get(condition)
    except AccountThird.DoesNotExist:
        # 这是第一次登陆，创建

        with transaction.atomic():
            account = AccountRegular.objects.create(
                platform=platform,
                uid=uid,
            )

    return account
