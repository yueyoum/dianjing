# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       timerd
Date Created:   2015-11-02 11:31
Description:

"""
import json
from urlparse import urljoin

import requests


def _setup(func):
    def deco(cls, *args, **kwargs):
        """

        :type cls: Timerd
        """
        if not cls._SETUP:
            cls.setup()

        return func(cls, *args, **kwargs)

    return deco


class Timerd(object):
    _SETUP = False

    URL_PING = ''
    URL_REGISTER = ''
    URL_QUERY = ''
    URL_CANCEL = ''

    @classmethod
    def setup(cls):
        from django.conf import settings

        cls.URL_PING = urljoin(settings.TIMERD_URL, '/ping/')
        cls.URL_REGISTER = urljoin(settings.TIMERD_URL, '/register/')
        cls.URL_QUERY = urljoin(settings.TIMERD_URL, '/query/')
        cls.URL_CANCEL = urljoin(settings.TIMERD_URL, '/cancel/')

        cls._SETUP = True

    @classmethod
    @_setup
    def ping(cls):
        req = requests.post(cls.URL_PING)
        assert req.ok is True

    @classmethod
    @_setup
    def register(cls, end, callback_path, callback_data):
        """

        :rtype : str
        """
        from django.conf import settings

        callback_url = urljoin(settings.SERVER_HOST, callback_path)
        data = {
            'end': end-1,   # 提前1秒完成，为了避免特殊情况：客户端先来查询状态，但timerd的回调还没到
            'url': callback_url,
            'data': json.dumps(callback_data)
        }

        req = requests.post(cls.URL_REGISTER, data=data)
        return req.json()['key']

    @classmethod
    @_setup
    def query(cls, key):
        """

        :rtype : int
        """
        data = {
            'key': key
        }

        req = requests.post(cls.URL_QUERY, data=data)
        return req.json()['ttl']

    @classmethod
    @_setup
    def cancel(cls, key):
        data = {
            'key': key
        }

        req = requests.post(cls.URL_CANCEL, data=data)
        assert req.ok is True
