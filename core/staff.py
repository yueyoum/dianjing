# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       staff
Date Created:   2015-07-09 17:07
Description:

"""

from dianjing.exception import GameException

from core.base import STAFF_ATTRS
from core.abstract import AbstractStaff
from core.mongo import MongoStaff, MongoRecruit
from core.resource import Resource
from core.common import CommonRecruitHot
from core.skill import SkillManager
from core.signals import recruit_staff_signal, staff_level_up_signal

from config import (
    ConfigStaff, ConfigStaffHot, ConfigStaffRecruit,
    ConfigStaffLevel, ConfigErrorMessage, ConfigClubLevel
)

from utils.message import MessagePipe

from protomsg.staff_pb2 import StaffRecruitNotify, StaffNotify, StaffRemoveNotify
from protomsg.staff_pb2 import RECRUIT_DIAMOND, RECRUIT_GOLD, RECRUIT_HOT, RECRUIT_NORMAL
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE


def staff_level_up_need_exp(staff_id, current_level):
    return ConfigStaffLevel.get(current_level).exp[ConfigStaff.get(staff_id).quality]


def staff_training_exp_need_gold(staff_id, staff_level):
    return staff_level * 1000


class Staff(AbstractStaff):
    __slots__ = ['id', 'level', 'exp', 'status', 'skills'] + STAFF_ATTRS

    def __init__(self, _id, data):
        super(Staff, self).__init__()

        self.id = _id  # 员工id
        self.level = data.get('level', 1)  # 员工等级
        self.exp = data.get('exp', 0)  # 员工经验
        # TODO 默认status
        self.status = data.get('status', 3)  # 状态 1:恶劣 2:低迷 3:一般 4:良好 5:优秀 6:GOD

        config_staff = ConfigStaff.get(self.id)
        self.race = config_staff.race
        self.quality = config_staff.quality

        self.jingong = config_staff.jingong + config_staff.jingong_grow * (self.level - 1) + data.get('jingong', 0)
        self.qianzhi = config_staff.qianzhi + config_staff.caozuo_grow * (self.level - 1) + data.get('qianzhi', 0)
        self.xintai = config_staff.xintai + config_staff.xintai_grow * (self.level - 1) + data.get('xintai', 0)
        self.baobing = config_staff.baobing + config_staff.baobing_grow * (self.level - 1) + data.get('baobing', 0)
        self.fangshou = config_staff.fangshou + config_staff.fangshou_grow * (self.level - 1) + data.get('fangshou', 0)
        self.yunying = config_staff.yunying + config_staff.yunying_grow * (self.level - 1) + data.get('yunying', 0)
        self.yishi = config_staff.yishi + config_staff.yunying_grow * (self.level - 1) + data.get('yishi', 0)
        self.caozuo = config_staff.caozuo + config_staff.caozuo_grow * (self.level - 1) + data.get('caozuo', 0)

        skills = data.get('skills', {})
        self.skills = {int(k): v['level'] for k, v in skills.iteritems()}


class StaffRecruit(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        doc = MongoRecruit.db(server_id).find_one({'_id': self.char_id}, {'_id': 1})
        if not doc:
            doc = MongoRecruit.document()
            doc['_id'] = self.char_id
            doc['tp'] = RECRUIT_HOT
            MongoRecruit.db(server_id).insert_one(doc)

    def get_self_refreshed_staffs(self):
        doc = MongoRecruit.db(self.server_id).find_one({'_id': self.char_id}, {'staffs': 1, 'tp': 1})
        tp = doc.get('tp', RECRUIT_HOT)
        if tp == RECRUIT_HOT:
            return []

        return doc['staffs']

    def get_hot_staffs(self):
        value = CommonRecruitHot.get(self.server_id)
        if not value:
            value = ConfigStaffHot.random_three()
            CommonRecruitHot.set(self.server_id, value)

        return value

    def refresh(self, tp):
        if tp == RECRUIT_HOT:
            staffs = self.get_hot_staffs()
        else:
            if tp == RECRUIT_NORMAL:
                refresh_id = 1
            elif tp == RECRUIT_GOLD:
                refresh_id = 2
            elif tp == RECRUIT_DIAMOND:
                refresh_id = 3
            else:
                raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

            check = {'message': u'Recruit refresh. type {0}'.format(tp)}
            config = ConfigStaffRecruit.get(refresh_id)
            if config.cost_type == 1:
                check['gold'] = -config.cost_value
            else:
                check['diamond'] = -config.cost_value

            doc = MongoRecruit.db(self.server_id).find_one(
                {'_id': self.char_id},
                {'times.{0}'.format(refresh_id): 1}
            )

            times = doc['times'].get(str(refresh_id), 0)
            is_first = False
            is_lucky = False
            if times == 0:
                is_first = True
            else:
                if times % config.lucky_times == 0:
                    is_lucky = True

            with Resource(self.server_id, self.char_id).check(**check):
                result = ConfigStaffRecruit.get(refresh_id).get_refreshed_staffs(first=is_first, lucky=is_lucky)
                staffs = []
                for quality, amount in result:
                    staffs.extend(ConfigStaff.get_random_ids_by_condition(amount, quality=quality))

        MongoRecruit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {
                '$set': {'tp': tp, 'staffs': staffs},
                '$inc': {'times.{0}'.format(tp): 1}
            }
        )

        self.send_notify(staffs=staffs, tp=tp)
        return staffs

    def recruit(self, staff_id):
        if not ConfigStaff.get(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id('STAFF_NOT_EXIST'))

        if StaffManger(self.server_id, self.char_id).has_staff(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id('STAFF_ALREADY_HAVE'))

        recruit_list = self.get_self_refreshed_staffs()
        if not recruit_list:
            recruit_list = self.get_hot_staffs()

        if staff_id not in recruit_list:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_RECRUIT_NOT_IN_LIST"))

        check = {"message": u"Recruit staff {0}".format(staff_id)}
        config = ConfigStaff.get(staff_id)
        if config.buy_type == 1:
            check['gold'] = -config.buy_cost
        else:
            check['diamond'] = -config.buy_cost

        with Resource(self.server_id, self.char_id).check(**check):
            StaffManger(self.server_id, self.char_id).add(staff_id)

        recruit_staff_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            staff_id=staff_id
        )

        self.send_notify()

    def send_notify(self, staffs=None, tp=None):
        if not staffs:
            staffs = self.get_self_refreshed_staffs()
            if not staffs:
                # 取common中的人气推荐
                staffs = self.get_hot_staffs()
                tp = RECRUIT_HOT
            else:
                tp = MongoRecruit.db(self.server_id).find_one({'_id': self.char_id}, {'tp': 1})['tp']

        already_recruited_staffs = StaffManger(self.server_id, self.char_id).get_all_staff_ids()

        notify = StaffRecruitNotify()
        notify.tp = tp
        for s in staffs:
            r = notify.recruits.add()
            r.staff_id = s
            r.has_recruit = s in already_recruited_staffs

        MessagePipe(self.char_id).put(msg=notify)


class StaffManger(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        doc = MongoStaff.db(server_id).find_one({'_id': self.char_id}, {'_id': 1})
        if not doc:
            doc = MongoStaff.document()
            doc['_id'] = self.char_id
            MongoStaff.db(server_id).insert_one(doc)

    @property
    def staffs_amount(self):
        return len(self.get_all_staffs())

    def get_all_staff_ids(self):
        return [int(i) for i in self.get_all_staffs().keys()]

    def get_all_staffs(self):
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, {'staffs': 1})
        return doc['staffs']

    def get_staff(self, staff_id):
        """

        :rtype : Staff
        """
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, {'staffs.{0}'.format(staff_id): 1})
        data = doc['staffs'].get(str(staff_id), None)
        if not data:
            return data
        return Staff(staff_id, data)

    def has_staff(self, staff_ids):
        if not isinstance(staff_ids, (list, tuple)):
            staff_ids = [staff_ids]

        projection = {'staffs.{0}'.format(i): 1 for i in staff_ids}

        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, projection)
        if not doc:
            return False

        staffs = doc.get('staffs', {})
        for staff_id in staff_ids:
            if str(staff_id) not in staffs:
                return False

        return True

    def add(self, staff_id, send_notify=True):
        from core.club import Club

        if not ConfigStaff.get(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        if self.has_staff(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_ALREADY_HAVE"))

        club_level = Club(self.server_id, self.char_id).level
        if self.staffs_amount >= ConfigClubLevel.get(club_level).max_staff_amount:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_AMOUNT_REACH_MAX_LIMIT"))

        doc = MongoStaff.document_staff()
        default_skills = ConfigStaff.get(staff_id).skill_ids

        skills = {str(sid): MongoStaff.document_staff_skill() for sid in default_skills}
        doc['skills'] = skills

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'staffs.{0}'.format(staff_id): doc}},
        )

        if send_notify:
            self.send_notify(staff_ids=[staff_id])
            SkillManager(self.server_id, self.char_id).send_notify(staff_id=staff_id)

    def remove(self, staff_id):
        from core.club import Club

        if not self.has_staff(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        if Club(self.server_id, self.char_id).is_staff_in_match(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_CAN_NOT_REMOVE_IN_MATCH"))

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$unset': {'staffs.{0}'.format(staff_id): 1}}
        )

        notify = StaffRemoveNotify()
        notify.id.append(staff_id)
        MessagePipe(self.char_id).put(msg=notify)

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

        this_staff = self.get_staff(staff_id)
        if not this_staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        # update
        level_updated = False
        current_level = this_staff.level
        current_exp = this_staff.exp + exp
        while True:
            need_exp = staff_level_up_need_exp(staff_id, current_level)

            next_level = ConfigStaffLevel.get(current_level).next_level
            if not next_level:
                if current_exp >= need_exp:
                    current_exp = need_exp - 1

                break

            if current_exp < need_exp:
                break

            current_exp -= need_exp
            current_level += 1
            level_updated = True

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {
                '$set': {
                    'staffs.{0}.exp'.format(staff_id): current_exp,
                    'staffs.{0}.level'.format(staff_id): current_level
                },

                '$inc': {
                    'staffs.{0}.jingong'.format(staff_id): jingong,
                    'staffs.{0}.qianzhi'.format(staff_id): qianzhi,
                    'staffs.{0}.xintai'.format(staff_id): xintai,
                    'staffs.{0}.baobing'.format(staff_id): baobing,
                    'staffs.{0}.fangshou'.format(staff_id): fangshou,
                    'staffs.{0}.yunying'.format(staff_id): yunying,
                    'staffs.{0}.yishi'.format(staff_id): yishi,
                    'staffs.{0}.caozuo'.format(staff_id): caozuo,
                },
            }
        )

        if level_updated:
            staff_level_up_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
                staff_id=staff_id,
                new_level=current_level
            )

        self.send_notify(staff_ids=[staff_id])

    @staticmethod
    def msg_staff(msg, sid, staff_data):
        staff = Staff(sid, staff_data)

        msg.id = staff.id
        msg.level = staff.level
        msg.cur_exp = staff.exp
        msg.max_exp = ConfigStaffLevel.get(staff.level).exp[staff.quality]
        msg.status = staff.status

        msg.jingong = int(staff.jingong)
        msg.qianzhi = int(staff.qianzhi)
        msg.xintai = int(staff.xintai)
        msg.baobing = int(staff.baobing)
        msg.fangshou = int(staff.fangshou)
        msg.yunying = int(staff.yunying)
        msg.yishi = int(staff.yishi)
        msg.caozuo = int(staff.caozuo)
        # TODO
        msg.zhimingdu = 100

        msg.training_exp_need_gold = staff_level_up_need_exp(staff.id, staff.level)

    def send_notify(self, staff_ids=None):
        if not staff_ids:
            projection = {'staffs': 1}
            act = ACT_INIT
        else:
            projection = {'staffs.{0}'.format(i): 1 for i in staff_ids}
            act = ACT_UPDATE

        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, projection)
        staffs = doc.get('staffs', {})

        notify = StaffNotify()
        notify.act = act
        for k, v in staffs.iteritems():
            s = notify.staffs.add()
            self.msg_staff(s, int(k), v)

        MessagePipe(self.char_id).put(msg=notify)
