# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       staff
Date Created:   2015-07-09 17:07
Description:

"""

from core.abstract import AbstractStaff
from core.db import get_mongo_db
from core.mongo import Document
from config import ConfigStaff, ConfigStaffHot, ConfigStaffRecruit

from utils.message import MessagePipe

from protomsg.staff_pb2 import StaffRecruitNotify, StaffNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE, ACT_ADD

class Staff(AbstractStaff):
    __slots__ = [
        'id', 'level', 'exp', 'status',
        'jingong', 'qianzhi', 'xintai', 'baobing',
        'fangshou', 'yunying', 'yishi', 'caozuo',
        'skills'
    ]

    def __init__(self, id, data):
        super(Staff, self).__init__()

        self.id = id
        self.level = data.get('level', 1)
        self.exp = data.get('exp', 0)
        # TODO 默认status
        self.status = data.get('status', 3)

        config_staff = ConfigStaff.get(self.id)
        self.race = config_staff.race

        self.jingong = config_staff.jingong + config_staff.jingong_grow * self.level + data.get('jingong', 0)
        self.qianzhi = config_staff.qianzhi + config_staff.caozuo_grow * self.level + data.get('qianzhi', 0)
        self.xintai = config_staff.xintai + config_staff.xintai_grow * self.level + data.get('xintai', 0)
        self.baobing = config_staff.baobing + config_staff.baobing_grow * self.level + data.get('baobing', 0)
        self.fangshou = config_staff.fangshou + config_staff.fangshou_grow * self.level + data.get('fangshou', 0)
        self.yunying = config_staff.yunying + config_staff.yunying_grow * self.level + data.get('yunying', 0)
        self.yishi = config_staff.yishi + config_staff.yunying_grow * self.level + data.get('yishi', 0)
        self.caozuo = config_staff.caozuo + config_staff.caozuo_grow * self.level + data.get('caozuo', 0)


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
                {'$set': {'tp': tp}, '$unset': {'staffs': 1}}
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
                {'$set': {'tp': tp, 'staffs': staffs}}
            )

        self.send_notify(staffs=staffs, tp=tp)


    def recruit(self, staff_id):
        # TODO check
        StaffManger(self.server_id, self.char_id).add(staff_id)
        self.send_notify()


    def send_notify(self, staffs=None, tp=None):
        if not staffs:
            staffs = self.get_normal_staff()
            if not staffs:
                # 取common中的人气推荐
                staffs = self.get_hot_staff()

            tp = self.mongo.recruit.find_one({'_id': self.char_id}, {'tp': 1})['tp']

        char = self.mongo.character.find_one({'_id': self.char_id}, {'staffs': 1})
        already_recruited_staffs = char.get('staffs', {})

        notify = StaffRecruitNotify()
        notify.tp = tp
        for s in staffs:
            r = notify.recruits.add()
            r.staff_id = s
            r.has_recruit = str(s) in already_recruited_staffs

        MessagePipe(self.char_id).put(msg=notify)


class StaffManger(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = get_mongo_db(server_id)


    def add(self, staff_id):
        doc = Document.get('staff')

        self.mongo.character.update_one(
            {'_id': self.char_id},
            {'$set': {'staffs.{0}'.format(staff_id): doc}}
        )

        self.send_notify(act=ACT_ADD, staffs={staff_id: doc})



    def msg_staff(self, msg, sid, staff):
        msg.id = sid
        # TODO
        msg.level = 1
        msg.cur_exp = 0
        msg.max_exp = 100
        msg.status = 1

        msg.jingong = 10
        msg.qianzhi = 10
        msg.xintai = 10
        msg.baobing = 10
        msg.fangshou = 10
        msg.yunying = 10
        msg.yishi = 10
        msg.caozuo = 10


    def send_notify(self, act=ACT_INIT, staffs=None):
        if not staffs:
            char = self.mongo.character.find_one({'_id': self.char_id}, {'staffs': 1})
            staffs = char.get('staffs', {})

        notify = StaffNotify()
        notify.act = act
        for k, v in staffs.iteritems():
            s = notify.staffs.add()
            self.msg_staff(s, int(k), v)

        MessagePipe(self.char_id).put(msg=notify)
