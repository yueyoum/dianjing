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
            raise RuntimeError("only can call redis.connect once!")

        db = 1 if settings.TEST else 0
        pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=db)
        cls.DB = redis.Redis(connection_pool=pool)
        cls.DB.ping()

    @classmethod
    def get(cls):
        """

        :rtype : redis.Redis
        """
        return cls.DB


class MongoDB(object):
    # 记录 host:port 和 db 之间的关系，为了去重复
    INSTANCES = {}
    # id: db
    DBS = {}

    @classmethod
    def connect(cls):
        if cls.DBS:
            raise RuntimeError("only can call mongo.connect once!")

        from apps.server.models import Server

        servers = Server.opened_servers()
        for s in servers:
            host = s.mongo_host.strip()
            port = int(s.mongo_port)
            mongo_instance_key = "{0}:{1}".format(host, port)
            if mongo_instance_key not in cls.INSTANCES:
                cls.INSTANCES[mongo_instance_key] = MongoClient(host=host, port=port)

            instance = cls.INSTANCES[mongo_instance_key]

            if not settings.TEST:
                db_name = s.mongo_db
            else:
                db_name = "{0}test".format(s.mongo_db)

            cls.DBS[s.id] = instance[db_name]

        print "MONGO"
        print cls.DBS

    @classmethod
    def get(cls, server_id):
        return cls.DBS[server_id]

    @classmethod
    def server_ids(cls):
        return cls.DBS.keys()


def connect():
    RedisDB.connect()
    MongoDB.connect()
