# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       session
Date Created:   2015-04-22 16:15
Description:

"""
import json

from core.db import RedisDB
from utils import crypto
from utils.functional import make_short_random_string


class GameSession(object):
    def __init__(self, **kwargs):
        self.__dict__['kwargs'] = kwargs

    def __getattr__(self, item):
        try:
            return self.kwargs[item]
        except KeyError:
            return None

    def __setattr__(self, key, value):
        self.__dict__['kwargs'][key] = value

    def serialize(self):
        return GameSession.dumps(**self.kwargs)

    @classmethod
    def dumps(cls, **kwargs):
        if not kwargs:
            raise RuntimeError("No kwargs to dumps")

        data = json.dumps(kwargs)
        return crypto.encrypt(data)

    @classmethod
    def loads(cls, data):
        data = crypto.decrypt(data)
        data = json.loads(data)
        return cls(**data)

    @classmethod
    def empty(cls):
        return cls()


class LoginID(object):
    ID_EXPIRE = 60 * 30 # 30 minutes

    @staticmethod
    def make_key(account_id):
        return 'login_id:{0}'.format(account_id)

    @classmethod
    def new(cls, account_id, value=None):
        key = LoginID.make_key(account_id)
        if not value:
            value = make_short_random_string()

        RedisDB.get(1).setex(key, value, cls.ID_EXPIRE)
        return value

    @classmethod
    def get(cls, account_id,):
        key = LoginID.make_key(account_id)
        return RedisDB.get(1).get(key)

    @classmethod
    def update_expire(cls, account_id):
        key = LoginID.make_key(account_id)
        RedisDB.get(1).expire(key, cls.ID_EXPIRE)
