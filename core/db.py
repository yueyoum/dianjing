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

_redis_pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
redis_client = redis.Redis(connection_pool=_redis_pool)
redis_client.ping()

_mongo_instance = {}
_mongo_dbs = {}

def mongo_connect():
    from apps.server.models import Server

    servers = Server.opened_servers()
    for s in servers:
        host = s.mongo_host.strip()
        port = int(s.mongo_port)
        mongo_instance_key = (host, port)
        if mongo_instance_key not in _mongo_instance:
            _mongo_instance[mongo_instance_key] = MongoClient(host=host, port=port)

        instance = _mongo_instance[mongo_instance_key]
        _mongo_dbs[s.id] = instance[s.mongo_db]

    print "MONGO"
    print _mongo_dbs


def get_mongo_db(server_id):
    return _mongo_dbs[server_id]

