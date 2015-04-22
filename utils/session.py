# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       session
Date Created:   2015-04-22 16:15
Description:

"""
import json
from utils import crypto

class GameSession(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __getattr__(self, item):
        return self.kwargs[item]


    @classmethod
    def dumps(cls, **kwargs):
        data = json.dumps(kwargs)
        return crypto.encrypt(data)

    @classmethod
    def loads(cls, data):
        data = crypto.decrypt(data)
        data = json.loads(data)
        return cls(**data)
