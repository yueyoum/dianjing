# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       cache
Date Created:   2015-07-02 16:04
Description:

"""
import cPickle
from cPickle import HIGHEST_PROTOCOL

from django.conf import settings
from core.db import RedisDB

CACHE_SECONDS = settings.REDIS_CACHE_SECONDS

def set(key, obj, expire=CACHE_SECONDS):
    data = cPickle.dumps(obj, HIGHEST_PROTOCOL)
    if expire:
        RedisDB.get().setex(key, data, expire)
    else:
        RedisDB.get().set(key, data)

def get(key):
    data = RedisDB.get().get(key)
    if data:
        return cPickle.loads(data)
    return None

def delete(key):
    RedisDB.get().delete(key)
