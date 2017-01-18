# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       account
Date Created:   2015-07-01 15:35
Description:

"""
import json
import hashlib

import requests

from django.conf import settings
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


def third_login(provider, platform, uid, param):
    if not provider or not platform or not uid:
        raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

    if provider == '1sdk':
        verify_1sdk(platform, uid, param)
    elif provider == 'stars-cloud':
        verify_stars_cloud(platform, uid, param)
    else:
        raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

    return get_or_create_third_account(provider, platform, uid)


def verify_1sdk(platform, uid, param):
    url = "http://sync.1sdk.cn/login/check.html"
    params = {
        'sdk': platform,
        'app': '{E15E4E08-795DB177}',
        'uin': uid,
        'sess': param
    }

    req = requests.get(url, params=params)
    if not req.ok or req.content != '0':
        raise GameException(ConfigErrorMessage.get_error_id("ACCOUNT_LOGIN_FAILURE"))


def verify_stars_cloud(platform, uid, param):
    ixToken, ixTime, ixSign = json.loads(param)
    AppId = settings.THIRD_PROVIDER['stars-cloud']['appid']
    pmSecret = settings.THIRD_PROVIDER['stars-cloud']['pmsecret']

    text = "{0}{1}{2}{3}{4}{5}".format(
        AppId, platform, uid, ixToken, ixTime, pmSecret
    )

    result = hashlib.md5(text).hexdigest()
    if result != ixSign:
        raise GameException(ConfigErrorMessage.get_error_id("ACCOUNT_LOGIN_FAILURE"))


def get_or_create_third_account(provider, platform, uid):
    try:
        condition = Q(provider=provider) & Q(platform=platform) & Q(uid=uid)
        account = AccountThird.objects.select_related('account').get(condition)
    except AccountThird.DoesNotExist:
        # 这是第一次登陆，创建
        with transaction.atomic():
            account = AccountThird.objects.create(
                provider=provider,
                platform=platform,
                uid=uid,
            )

    return account
