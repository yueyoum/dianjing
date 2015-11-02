# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       timerd
Date Created:   2015-11-02 11:31
Description:

"""
import json
from urlparse import urljoin
from django.conf import settings

import requests

class Timerd(object):
    URL_REGISTER = urljoin(settings.TIMERD_URL, '/register/')
    URL_QUERY = urljoin(settings.TIMERD_URL, '/query/')
    URL_CANCEL = urljoin(settings.TIMERD_URL, '/cancel/')

    @classmethod
    def register(cls, end, callback_path, callback_data):
        """

        :rtype : str
        """

        callback_url = urljoin(settings.SERVER_HOST, callback_path)
        data = {
            'end': end,
            'url': callback_url,
            'data': json.dumps(callback_data)
        }

        req = requests.post(cls.URL_REGISTER, data=data)
        return req.json()['key']

    @classmethod
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
    def cancel(cls, key):
        data = {
            'key': key
        }

        req = requests.post(cls.URL_CANCEL, data=data)
        assert req.ok is True
        return None

