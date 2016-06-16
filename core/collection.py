# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       collection
Date Created:   2016-05-27 15-11
Description:

"""

from core.mongo import MongoStaffCollection

from config import ConfigCollection

from utils.message import MessagePipe

from protomsg.collection_pb2 import CollectionNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE


class Collection(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.doc = MongoStaffCollection.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoStaffCollection.document()
            self.doc['_id'] = self.char_id
            MongoStaffCollection.db(self.server_id).insert_one(self.doc)

    def add(self, staff_id, send_notify=True):
        from core.club import Club

        if staff_id in self.doc['staffs']:
            return

        if staff_id not in ConfigCollection.INSTANCES:
            return

        self.doc['staffs'].append(staff_id)
        MongoStaffCollection.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$push': {'staffs': staff_id}}
        )

        self.send_notify(staff_ids=[staff_id])
        Club(self.server_id, self.char_id, load_staffs=False).force_load_staffs(send_notify=send_notify)

    def get_talent_effects(self):
        return [ConfigCollection.get(i).talent_effect_id for i in self.doc['staffs']]

    def send_notify(self, staff_ids=None):
        if staff_ids:
            act = ACT_UPDATE
        else:
            act = ACT_INIT
            staff_ids = self.doc['staffs']

        notify = CollectionNotify()
        notify.act = act
        notify.collected_ids.extend(staff_ids)
        MessagePipe(self.char_id).put(msg=notify)
