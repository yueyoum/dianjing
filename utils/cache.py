# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       cache
Date Created:   2015-07-02 16:04
Description:

"""
import cPickle
from cPickle import HIGHEST_PROTOCOL

from core.db import RedisDB

CACHE_SECONDS = 3600 * 6    # 6 hours

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

def flush():
    RedisDB.get().flushdb()