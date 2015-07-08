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
from core.db import redis_client

CACHE_SECONDS = settings.REDIS_CACHE_SECONDS

def set(key, obj, expire=CACHE_SECONDS):
    data = cPickle.dumps(obj, HIGHEST_PROTOCOL)
    if expire:
        redis_client.setex(key, data, expire)
    else:
        redis_client.set(key, data)

def get(key):
    data = redis_client.get(key)
    if data:
        return cPickle.loads(data)
    return None

def delete(key):
    redis_client.delete(key)
