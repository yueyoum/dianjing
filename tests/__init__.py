# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       __init__.py
Date Created:   2015-08-04 14:45
Description:

"""


def setup():
    import os
    os.environ['DIANJING_TEST'] = '1'

    import dianjing.wsgi

    teardown()

    from core.mongo import MongoCharacter
    from core.character import Character
    Character.create(1, 1, "one", "club_one", 1)
    MongoCharacter.db(1).update_one(
        {'_id': 1},
        {'$set': {
            'club.gold': 0,
            'club.diamond': 0
        }}
    )


def teardown():
    from core.db import MongoDB, RedisDB
    mongo = MongoDB.get(1)
    mongo.client.drop_database(mongo.name)

    RedisDB.get().flushdb()

