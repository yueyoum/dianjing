# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       staff
Date Created:   2015-07-09 17:07
Description:

"""

from core.db import get_mongo_db
from core.mongo import Document
from config import ConfigStaff, ConfigStaffHot, ConfigStaffRecruit

from utils.message import MessagePipe

from protomsg.staff_pb2 import StaffRecruitNotify

class StaffRecruit(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.mongo = get_mongo_db(self.server_id)

        data = self.mongo.recruit.find_one({'_id': self.char_id}, {'_id': 1})
        if not data:
            doc = Document.get("recruit")
            doc['_id'] = self.char_id
            doc['tp'] = 1
            self.mongo.recruit.insert_one(doc)


    def get_normal_staff(self):
        data = self.mongo.recruit.find_one({'_id': self.char_id}, {'staffs': 1})
        return data.get('staffs', [])


    def get_hot_staff(self):
        data = self.mongo.common.find_one({'_id': 'recruit_hot'}, {'value': 1})
        if not data or not data.get('value', []):
            staffs = ConfigStaffHot.random_three()
            self.mongo.common.update_one(
                {'_id': 'recruit_hot'},
                {'$set': {'value': staffs}},
                upsert=True
            )
            return staffs

        return data['value']


    def refresh(self, tp):
        if tp == 1:
            staffs = self.get_hot_staff()
            self.mongo.recruit.update_one(
                {'_id': self.char_id},
                {'$set': {'tp': tp}}
            )
        else:
            if tp == 2:
                refresh_id = 1
            elif tp == 3:
                refresh_id = 2
            elif tp == 4:
                refresh_id = 3
            else:
                raise RuntimeError()

            result = ConfigStaffRecruit.get(refresh_id).get_refreshed_staffs()
            staffs = []
            for quality, amount in result:
                staffs.extend( ConfigStaff.get_random_ids_by_condition(amount, quality=quality) )

            self.mongo.recruit.update_one(
                {'_id': self.char_id},
                {'$set': {
                    {'tp': tp},
                    {'staffs': staffs}
                }}
            )

        self.send_notify(staffs=staffs)


    def recruit(self, staff_id):
        # TODO check
        self.mongo.character.update_one(
            {'_id': self.char_id},
            {'$set': {'staffs.{0}'.format(staff_id), {}}}
        )

        self.send_notify()


    def send_notify(self, staffs=None):
        if not staffs:
            staffs = self.get_normal_staff()
            if not staffs:
                # 取common中的人气推荐
                staffs = self.get_hot_staff()

        char = self.mongo.character.find_one({'_id': self.char_id}, {'staffs': 1})
        already_recruited_staffs = char.get('staffs', {})

        notify = StaffRecruitNotify()
        for s in staffs:
            r = notify.recruits.add()
            r.staff_id = s
            r.has_recruit = str(s) in already_recruited_staffs

        MessagePipe(self.char_id).put(msg=notify)

