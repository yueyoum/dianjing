# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       common
Date Created:   2015-08-05 10:23
Description:

"""

from core.mongo import MongoCommon


class BaseCommon(object):
    ID = None

    @classmethod
    def get(cls, server_id):
        doc = MongoCommon.db(server_id).find_one({'_id': cls.ID})
        return doc.get('value', None) if doc else None

    @classmethod
    def set(cls, server_id, value):
        MongoCommon.db(server_id).update_one(
            {'_id': cls.ID},
            {'$set': {'value': value}},
            upsert=True
        )

    @classmethod
    def delete(cls, server_id):
        MongoCommon.db(server_id).delete_one({'_id': cls.ID})


class CommonChat(BaseCommon):
    ID = 'chat'


class CommonTask(BaseCommon):
    ID = 'task'


class CommonLadderStore(BaseCommon):
    ID = 'ladder_store'


class CommonTrainingMatchStore(BaseCommon):
    ID = 'training_match_store'