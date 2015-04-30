# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       db
Date Created:   2015-04-29 23:16
Description:

"""

import redis

from django.conf import settings

_redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0
)

redis_client = redis.Redis(connection_pool=_redis_pool)
