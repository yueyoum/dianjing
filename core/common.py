# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       common
Date Created:   2015-08-05 10:23
Description:

"""

from core.db import MongoDB

class Common(object):
    @classmethod
    def get(cls, server_id, _id):
        doc = MongoDB.get(server_id).common.find_one({'_id': _id})
        return doc.get('value', None) if doc else None

    @classmethod
    def set(cls, server_id, _id, value):
        MongoDB.get(server_id).common.update_one(
            {'_id': _id},
            {'$set': {'value': value}},
            upsert=True
        )

    @classmethod
    def delete(cls, server_id, _id):
        MongoDB.get(server_id).common.delete_one({'_id': _id})
