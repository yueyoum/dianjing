# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       common
Date Created:   2015-08-05 10:23
Description:

"""

from core.mongo import MongoCommon


class BaseCommon(object):
    __slots__ = ['server_id']

    def __init__(self, server_id):
        self.server_id = server_id

    def get_id(self):
        raise NotImplementedError()

    def get(self):
        _id = self.get_id()
        doc = MongoCommon.db(self.server_id).find_one({'_id': _id})
        return doc.get('value', None) if doc else None

    def set(self, value):
        _id = self.get_id()
        MongoCommon.db(self.server_id).update_one(
            {'_id': _id},
            {'$set': {'value': value}},
            upsert=True
        )

    def push(self, value, slice_amount=None):
        if isinstance(value, (list, tuple)):
            value_list = list(value)
        else:
            value_list = [value]

        updater = {
            '$push': {
                'value': {
                    '$each': value_list,
                }
            }
        }

        if slice_amount:
            updater['$push']['value']['$slice'] = -slice_amount

        _id = self.get_id()
        MongoCommon.db(self.server_id).update_one(
            {'_id': _id},
            updater,
            upsert=True
        )

    def delete(self):
        _id = self.get_id()
        MongoCommon.db(self.server_id).delete_one({'_id': _id})


class CommonPublicChat(BaseCommon):
    def get_id(self):
        return 'chat'


class CommonUnionChat(BaseCommon):
    __slots__ = ['union_id']

    def __init__(self, server_id, union_id):
        super(CommonUnionChat, self).__init__(server_id)
        self.union_id = union_id

    def get_id(self):
        return 'union_chat_{0}'.format(self.union_id)
