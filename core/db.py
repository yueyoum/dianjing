# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       db
Date Created:   2015-04-29 23:16
Description:

"""

import redis
from pymongo import MongoClient
from django.conf import settings


class RedisDB(object):
    DBS = {}
    """:type: dict[int, redis.Redis]"""

    # 分开的原因是 可以单独清空某个db
    # db 0: 默认db，常规使用
    # db 1: login id

    @classmethod
    def connect(cls):
        if cls.DBS:
            return

        cls.DBS[0] = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        cls.DBS[0].ping()

        cls.DBS[1] = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=1)

    @classmethod
    def get(cls, db=0):
        """

        :rtype : redis.Redis
        """

        if not cls.DBS:
            cls.connect()

        return cls.DBS[db]


class MongoDB(object):
    # id: db
    DBS = {}
    """:type: dict[int, pymongo.database.Database]"""

    @classmethod
    def connect(cls):
        if cls.DBS:
            return

        for mongo_config in settings.MONGODB:
            if mongo_config['user']:
                mongo_url = "mongodb://{0}:{1}@{2}:{3}".format(
                    mongo_config['user'], mongo_config['password'],
                    mongo_config['host'], mongo_config['port']
                )
            else:
                mongo_url = "mongodb://{0}:{1}".format(
                    mongo_config['host'], mongo_config['port'],
                )

            client = MongoClient(mongo_url)
            for i in range(mongo_config['sid-min'], mongo_config['sid-max'] + 1):
                db = '{0}{1}'.format(settings.MONGODB_PREFIX, i)
                cls.DBS[i] = client[db]

    @classmethod
    def get(cls, server_id):
        if not cls.DBS:
            cls.connect()

        return cls.DBS[server_id]
