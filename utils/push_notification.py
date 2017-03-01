# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       push_notification
Date Created:   2017-03-01 12:00
Description:

"""

import os
import json
import hashlib
import arrow
import requests

from django.conf import settings
from django.db.models import Q

from apps.account.models import AccountLoginLog
from apps.character.models import Character as ModelCharacter
from apps.account.models import GeTuiClientID

from core.energy import Energy

from utils import cache
from utils.operation_log import OperationLog
from utils.functional import get_start_time_of_today


class GeTui(object):
    __slots__ = ['account_id']

    CACHE_KEY = 'getui_auth_token'
    CACHE_EXPIRE = 3600 * 6

    def __init__(self, account_id):
        self.account_id = account_id

    @classmethod
    def job_of_energy_notification(cls):
        # 找最近登陆的，并且在多少时间内没操作的（认为已经下线了
        account_ids = AccountLoginLog.get_recent_login_account_ids(2)
        action_limit = arrow.utcnow().timestamp - 60 * 30

        count = 0
        for account_id, server_id in account_ids.iteritems():
            model_char = ModelCharacter.objects.get(Q(account_id=account_id) & Q(server_id=server_id))
            char_id = model_char.id

            if OperationLog.get_char_last_action_at(server_id, char_id) > action_limit:
                continue

            if not Energy(server_id, char_id).is_full():
                continue

            title = u"体力满了"
            content = u"您在 {0} 服的角色 {1} 体力满了，赶快上线吧".format(server_id, model_char.name)

            pushed = GeTui(account_id).push_of_energy(title, content)
            if pushed:
                count += 1

        return count

    @classmethod
    def job_of_login_notification(cls):
        today = get_start_time_of_today()
        yesterday = today.replace(days=-1)
        day_before_yesterday = yesterday.replace(days=-1)

        day_before_yesterday_logged_account_ids = set()

        condition = Q(login_at__gte=day_before_yesterday.format("YYYY-MM-DD HH:mm:ssZ")) & \
                    Q(login_at__lt=yesterday.format("YYYY-MM-DD HH:mm:ssZ"))

        for log in AccountLoginLog.objects.filter(condition):
            day_before_yesterday_logged_account_ids.add(log.account_id)

        yesterday_to_now_logged_account_ids = set()
        condition = Q(login_at__gte=yesterday.format("YYYY-MM-DD HH:mm:ssZ")) & \
                    Q(login_at__lt=arrow.utcnow().format("YYYY-MM-DD HH:mm:ssZ"))

        for log in AccountLoginLog.objects.filter(condition):
            yesterday_to_now_logged_account_ids.add(log.account_id)

        not_logged_account_ids = day_before_yesterday_logged_account_ids - yesterday_to_now_logged_account_ids

        title = u"你已经一天没有上线了"
        content = u"赶快上线吧"
        count = 0

        for account_id in not_logged_account_ids:
            pushed = GeTui(account_id).push_of_login(title, content)
            if pushed:
                count += 1

        return count

    @classmethod
    def generate_auth_token(cls):
        url = 'https://restapi.getui.com/v1/{0}/auth_sign'.format(settings.GETUI_APPID)
        headers = {'Content-Type': 'application/json'}
        timestamp = arrow.utcnow().timestamp * 1000
        sign = hashlib.sha256(
            '{0}{1}{2}'.format(settings.GETUI_APPKEY, timestamp, settings.GETUI_MASTERSECRET)).hexdigest()

        data = {
            'sign': sign,
            'timestamp': timestamp,
            'appkey': settings.GETUI_APPKEY,
        }

        r = requests.post(url, headers=headers, data=json.dumps(data))
        return r.json()['auth_token']

    @classmethod
    def get_auth_token(cls):
        token = cache.get(cls.CACHE_KEY)
        if not token:
            token = cls.generate_auth_token()
            cache.set(cls.CACHE_KEY, token, expire=cls.CACHE_EXPIRE)

        return token

    def set_client_id(self, client_id):
        try:
            m = GeTuiClientID.objects.get(id=self.account_id)
            m.client_id = client_id
            m.save()
        except GeTuiClientID.DoesNotExist:
            GeTuiClientID.objects.create(
                id=self.account_id,
                client_id=client_id
            )

    def push_of_energy(self, title, content):
        key = 'getui:energy:{0}'.format(self.account_id)

        if cache.get(key):
            return None

        result = self._push(title, content)
        self._set_cache(key)

        return result

    def push_of_login(self, title, content):
        key = 'getui:login:{0}'.format(self.account_id)

        if cache.get(key):
            return None

        result = self._push(title, content)
        self._set_cache(key)

        return result

    def _set_cache(self, key):
        today = get_start_time_of_today()
        tomorrow = today.replace(days=1)
        expire = tomorrow.timestamp - arrow.utcnow().timestamp
        cache.set(key, 1, expire=expire)

    def _push(self, title, content):
        try:
            m = GeTuiClientID.objects.get(id=self.account_id)
            client_id = m.client_id
        except GeTuiClientID.DoesNotExist:
            return None

        url = 'https://restapi.getui.com/v1/{0}/push_single'.format(settings.GETUI_APPID)
        headers = {
            'Content-Type': 'application/json',
            'authtoken': self.get_auth_token(),
        }

        data = {
            'message': {
                'appkey': settings.GETUI_APPKEY,
                'msgtype': 'notification',
            },
            'notification': {
                'title': title,
                'text': content,
                'transmission_type': True,
            },
            'cid': client_id,
            'requestid': os.urandom(8).encode('hex')
        }

        r = requests.post(url, headers=headers, data=json.dumps(data))
        return r.json()
