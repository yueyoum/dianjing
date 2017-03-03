# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       mark
Date Created:   2017-03-03 11:25
Description:    记录标志

"""

import arrow
from core.mongo import MongoMark


class BaseMark(object):
    __slots__ = ['server_id']

    def __init__(self, server_id):
        self.server_id = server_id

    def get_id(self):
        raise NotImplementedError()

    def mark(self):
        doc = MongoMark.document()
        doc['_id'] = self.get_id()
        doc['create_at'] = arrow.utcnow().timestamp
        MongoMark.db(self.server_id).insert_one(doc)

    def is_marked(self):
        _id = self.get_id()
        doc = MongoMark.db(self.server_id).find_one({'_id': _id})
        return doc is not None

    def delete(self):
        _id = self.get_id()
        MongoMark.db(self.server_id).delete_one({'_id': _id})


class WinningChatApprovalMark(BaseMark):
    __slots__ = ['char_id', 'msg_id']

    def __init__(self, server_id, char_id, msg_id):
        super(WinningChatApprovalMark, self).__init__(server_id)
        self.char_id = char_id
        self.msg_id = msg_id

    def get_id(self):
        return '{0}_{1}'.format(self.char_id, self.msg_id)
