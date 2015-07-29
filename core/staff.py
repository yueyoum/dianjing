# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       staff
Date Created:   2015-07-09 17:07
Description:

"""

import arrow

from core.abstract import AbstractStaff
from core.db import get_mongo_db
from core.mongo import Document
from core.resource import Resource
from core.skill import SkillManager

from config import ConfigStaff, ConfigStaffHot, ConfigStaffRecruit, ConfigTraining, ConfigStaffLevel

from utils.message import MessagePipe

from protomsg.staff_pb2 import StaffRecruitNotify, StaffNotify, StaffRemoveNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE

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
        self.quality = config_staff.quality

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
        default_skills = ConfigStaff.get(staff_id).skill_ids

        skills = {str(sid): Document.get('skill') for sid in default_skills}
        doc['skills'] = skills

        self.mongo.character.update_one(
            {'_id': self.char_id},
            {'$set': {'staffs.{0}'.format(staff_id): doc}}
        )

        self.send_notify(act=ACT_UPDATE, staff_ids=[staff_id])
        SkillManager(self.server_id, self.char_id).send_notify(act=ACT_INIT, staff_id=staff_id)


    def remove(self, staff_id):
        self.mongo.character.update_one(
            {'_id': self.char_id},
            {'$unset': {'staffs.{0}'.format(staff_id): 1}}
        )

        notify = StaffRemoveNotify()
        notify.id.append(staff_id)

        MessagePipe(self.char_id).put(msg=notify)


    def training_start(self, staff_id, training_id):
        # TODO check training_id own ?
        # TODO check staff exists ?

        data = {
            'training_id': training_id,
            'start_at': arrow.utcnow().timestamp
        }

        key = 'staffs.{0}.trainings'.format(staff_id)

        self.mongo.character.update_one(
            {'_id': self.char_id},
            {'$push': {key: data}}
        )

        self.send_notify(act=ACT_UPDATE, staff_ids=[staff_id])


    def training_get_reward(self, staff_id, slot_id):
        # TODO
        key = "staffs.{0}.trainings".format(staff_id)

        char = self.mongo.character.find_one({'_id': self.char_id}, {key: 1})
        trainings = char['staffs'][str(staff_id)]['trainings']
        data =  trainings.pop(slot_id)

        self.mongo.character.update_one(
            {'_id': self.char_id},
            {'$set': {key: trainings}}
        )

        self.send_notify(act=ACT_UPDATE, staff_ids=[staff_id])

        config_training = ConfigTraining.get(data['training_id'])
        if config_training.tp == 3:
            # 技能
            SkillManager(self.server_id, self.char_id).add_level(staff_id, config_training.skill_id, config_training.skill_level)
        else:
            Resource(self.server_id, self.char_id).add_from_package_id(config_training.package, staff_id)


    def update(self, staff_id, **kwargs):
        exp = kwargs.get('exp', 0)
        jingong = kwargs.get('jingong', 0)
        qianzhi = kwargs.get('qianzhi', 0)
        xintai = kwargs.get('xintai', 0)
        baobing = kwargs.get('baobing', 0)
        fangshou = kwargs.get('fangshou', 0)
        yunying = kwargs.get('yunying', 0)
        yishi = kwargs.get('yishi', 0)
        caozuo = kwargs.get('caozuo', 0)

        char = self.mongo.character.find_one({'_id': self.char_id}, {'staffs.{0}'.format(staff_id): 1})
        this_staff = char['staffs'][str(staff_id)]

        next_level = ConfigStaffLevel.get(this_staff['level']).next_level
        if next_level:
            new_exp = this_staff['exp'] + exp
            level_up_need_exp = ConfigStaffLevel.get(this_staff['level']).exp[ConfigStaff.get(staff_id).quality]
            if new_exp >= level_up_need_exp:
                new_exp -= level_up_need_exp
                new_level = next_level
            else:
                new_level = this_staff['level']
        else:
            new_exp = this_staff['exp']
            new_level = this_staff['level']

        self.mongo.character.update_one(
            {'_id': self.char_id},
            {'$inc': {
                'staffs.{0}.exp'.format(staff_id): new_exp,
                'staffs.{0}.level'.format(staff_id): new_level,
                'staffs.{0}.jingong'.format(staff_id): jingong,
                'staffs.{0}.qianzhi'.format(staff_id): qianzhi,
                'staffs.{0}.xintai'.format(staff_id): xintai,
                'staffs.{0}.baobing'.format(staff_id): baobing,
                'staffs.{0}.fangshou'.format(staff_id): fangshou,
                'staffs.{0}.yunying'.format(staff_id): yunying,
                'staffs.{0}.yishi'.format(staff_id): yishi,
                'staffs.{0}.caozuo'.format(staff_id): caozuo,
            }}
        )

        self.send_notify(act=ACT_UPDATE, staff_ids=[staff_id])


    def msg_staff(self, msg, sid, staff_data):
        staff = Staff(sid, staff_data)

        msg.id = staff.id
        msg.level = staff.level
        msg.cur_exp = staff.exp
        msg.max_exp = ConfigStaffLevel.get(staff.level).exp[staff.quality]
        msg.status = staff.status

        msg.jingong = staff.jingong
        msg.qianzhi = staff.qianzhi
        msg.xintai = staff.xintai
        msg.baobing = staff.baobing
        msg.fangshou = staff.fangshou
        msg.yunying = staff.yunying
        msg.yishi = staff.yishi
        msg.caozuo = staff.caozuo

        training = staff_data.get('trainings', [])
        for i in range(5):
            msg_training_slot = msg.training_slots.add()
            msg_training_slot.slot_id = i

            try:
                tr = training[i]
                msg_training_slot.training_id = tr['training_id']
                msg_training_slot.end_at = tr['start_at'] + ConfigTraining.get(tr['training_id']).minutes * 60
                if msg_training_slot.end_at <= arrow.utcnow().timestamp:
                    msg_training_slot.status = 5
                else:
                    msg_training_slot.status = 4

            except IndexError:
                msg_training_slot.status = 2

        # 只有一个处于正在训练的状态
        in_queue = False
        for i in msg.training_slots:
            if i.status == 4:
                if not in_queue:
                    in_queue = True
                else:
                    i.status = 3


    def send_notify(self, act=ACT_INIT, staff_ids=None):
        if not staff_ids:
            projection = {'staffs': 1}
        else:
            projection = {'staffs.{0}'.format(i): 1 for i in staff_ids}

        char = self.mongo.character.find_one({'_id': self.char_id}, projection)
        staffs = char.get('staffs', {})

        notify = StaffNotify()
        notify.act = act
        for k, v in staffs.iteritems():
            s = notify.staffs.add()
            self.msg_staff(s, int(k), v)

        MessagePipe(self.char_id).put(msg=notify)
