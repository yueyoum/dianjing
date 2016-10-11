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
    DB = None

    @classmethod
    def connect(cls):
        if cls.DB:
            return

        pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        cls.DB = redis.Redis(connection_pool=pool)
        cls.DB.ping()

    @classmethod
    def get(cls):
        """

        :rtype : redis.Redis
        """

        if not cls.DB:
            cls.connect()

        return cls.DB


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
                    mongo_config['user'], mongo_config['password'],
                )

            client = MongoClient(mongo_url)
            for i in range(mongo_config['sid-min'], mongo_config['sid-max'] + 1):
                db = 'dianjing{0}'.format(i)
                cls.DBS[i] = client[db]

    @classmethod
    def get(cls, server_id):
        if not cls.DBS:
            cls.connect()

        return cls.DBS[server_id]
