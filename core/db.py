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

        db = 1 if settings.TEST else 0
        pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=db)
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
    # 记录 host:port 和 db 之间的关系，为了去重复
    INSTANCES = {}
    """:type: dict[str, MongoClient]"""
    # id: db
    DBS = {}
    """:type: dict[int, pymongo.database.Database]"""

    @classmethod
    def connect(cls):
        from apps.server.models import Server

        if cls.DBS:
            return

        servers = Server.opened_servers()
        for s in servers:
            host = s.mongo_host.strip()
            port = int(s.mongo_port)
            mongo_instance_key = "{0}:{1}".format(host, port)
            if mongo_instance_key not in cls.INSTANCES:

                if settings.MONGODB_USER:
                    mongo_url = "mongodb://{0}:{1}@{2}:{3}".format(
                        settings.MONGODB_USER, settings.MONGODB_PASSWORD, host, port
                    )
                else:
                    mongo_url = "mongodb://{0}:{1}".format(host, port)

                cls.INSTANCES[mongo_instance_key] = MongoClient(mongo_url)

            instance = cls.INSTANCES[mongo_instance_key]

            if not settings.TEST:
                db_name = s.mongo_db
            else:
                db_name = "{0}test".format(s.mongo_db)

            cls.DBS[s.id] = instance[db_name]


    @classmethod
    def get(cls, server_id):
        if not cls.DBS:
            cls.connect()

        return cls.DBS[server_id]
