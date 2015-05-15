# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       core
Date Created:   2015-04-28 15:15
Description:

"""

import json
import random
import arrow

from dianjing.exception import GameException

from apps.club.models import Club
from apps.staff.models import Staff as ModelStaff, StaffTraining as ModelStaffTraining
from apps.staff.property import StaffProperty
from utils.message import MessagePipe

from protomsg.staff_pb2 import Staff as ProtocolStaff
from protomsg.staff_pb2 import StaffNotify, StaffRemoveNotify
from protomsg.common_pb2 import ACT_ADD, ACT_INIT, ACT_UPDATE

from config import CONFIG


MAX_STATUS = max(CONFIG.STAFF_STATUS.keys())

class StaffManager(object):
    def __init__(self, char_id):
        self.char_id = char_id
        self.club_id = Club.objects.get(char_id=self.char_id).id


    def add(self, oid, send_notify=True):
        if oid not in CONFIG.STAFF:
            raise GameException( CONFIG.ERRORMSG["STAFF_NOT_EXIST"].id )

        try:
            s = ModelStaff.objects.create(
                club_id=self.club_id,
                oid=oid,
            )
        except:
            raise GameException( CONFIG.ERRORMSG["STAFF_ALREADY_HAVE"].id )

        staff = Staff.new(self.char_id, s.id)
        if send_notify:
            msg = StaffNotify()
            msg.act = ACT_ADD
            msg_staff = msg.staffs.add()
            msg_staff.MergeFrom(staff.make_protocol_msg())

            MessagePipe(self.char_id).put(msg=msg)

        return staff


    def remove(self, staff_id):
        pass


    def training_start(self, staff_id, training_id):
        try:
            ModelStaff.objects.get(id=staff_id)
        except ModelStaff.DoesNotExist:
            raise GameException( CONFIG.ERRORMSG["STAFF_NOT_EXIST"].id )

        if training_id not in CONFIG.TRAINING:
            raise GameException( CONFIG.ERRORMSG["TRAINING_NOT_EXIST"].id )

        # training slots check
        ModelStaffTraining.objects.create(
            staff_id=staff_id,
            training_id=training_id,
        )

        s = Staff.new(self.char_id, staff_id)
        msg = StaffNotify()
        msg.act = ACT_UPDATE
        msg_staff = msg.staffs.add()
        msg_staff.MergeFrom(s.make_protocol_msg())

        MessagePipe(self.char_id).put(msg=msg)


    def training_get_reward(self, slot_id):
        try:
            tr = ModelStaffTraining.objects.get(id=slot_id)
        except ModelStaffTraining.DoesNotExist:
            raise GameException( CONFIG.ERRORMSG["TRAINING_NOT_EXIST"].id )

        info = TrainingInfo(tr.training_id, tr.start_at)
        if not info.is_end:
            raise GameException( CONFIG.ERRORMSG["TRAINING_NOT_FINISHED"].id )

        staff_id = tr.staff_id
        training_id = tr.training_id
        # delete this training
        tr.delete()

        staff = Staff.new(self.char_id, staff_id)
        staff.add_reward_from_training(training_id)

        # send update notify
        msg = StaffNotify()
        msg.act = ACT_UPDATE
        msg_staff = msg.staffs.add()
        msg_staff.MergeFrom(staff.make_protocol_msg())

        MessagePipe(self.char_id).put(msg=msg)


    def send_notify(self):
        msg = StaffNotify()
        msg.act = ACT_INIT
        for s in ModelStaff.objects.filter(char_id=self.char_id):
            msg_staff = msg.staffs.add()
            msg_staff.MergeFrom( Staff.new(self.char_id, s.id).make_protocol_msg() )

        MessagePipe(self.char_id).put(msg=msg)



class Staff(object):
    @staticmethod
    def new(char_id, staff_id):
        # TODO cache
        return Staff(char_id, staff_id)

    def __init__(self, char_id, staff_id):
        self.char_id = char_id
        self.id = staff_id

        self.load_from_db()


    def load_from_db(self):
        s = ModelStaff.objects.get(id=self.id)

        self.oid = s.oid
        self.level = s.level
        self.exp = s.exp
        self.status = s.status

        self.skills = json.loads(s.skills)

        config_s = CONFIG.STAFF[self.oid]

        property_add = json.loads(s.property_add)
        status_value = CONFIG.STAFF_STATUS[self.status].value
        status_multiple = 1 + status_value / 100.0

        def _cal_property(name):
            short_name = StaffProperty.name_to_short_name(name)
            base = getattr(config_s, name) + getattr(config_s, "%s_grow" % name) * self.level + property_add[short_name]

            base *= status_multiple
            return base


        for k in StaffProperty.NAME_DICT.keys():
            v = _cal_property(k)
            setattr(self, k, v)


    def get_trainings_info(self):
        # trainings = [(slot_id, training_id, end_at, is_end)]
        trainings = []
        for tr in ModelStaffTraining.objects.filter(staff_id=self.id).order_by('start_at'):
            info = TrainingInfo(tr.training_id, tr.start_at)

            trainings.append(
                (tr.id, tr.training_id, info.end_at, info.is_end)
            )

        return trainings

    def add_property(self, key, value):
        s = ModelStaff.objects.get(id=self.id)

        property_add = json.loads(s.property_add)
        property_add[key] += value
        s.property_add = json.dumps(property_add)
        s.save()


    def add_reward_from_training(self, training_id):
        from apps.club.core import ClubManager

        training = CONFIG.TRAINING[training_id]

        staff = ModelStaff.objects.get(id=self.id)
        if training.reward_type == 1:
            # 经验
            staff.exp += training.reward_value
            # TODO level up
            staff.save()
        elif training.reward_type == 2:
            # 软妹币
            ClubManager(self.char_id).add(gold=training.reward_value)
        elif training.reward_type == 3:
            # 状态
            staff.status += training.reward_value
            if staff.status > MAX_STATUS:
                staff.status = MAX_STATUS

            staff.save()
        elif training.reward_type == 10:
            # 随机属性
            property_add = json.loads(staff.property_add)
            p = random.choice(property_add.keys())
            self.add_property(p, training.reward_value)
        elif training.reward_type == 11:
            # 进攻 jg
            self.add_property('jg', training.reward_value)
        elif training.reward_type == 12:
            # 牵制 qz
            self.add_property('qz', training.reward_value)
        elif training.reward_type == 13:
            # 心态 xt
            self.add_property('xt', training.reward_value)
        elif training.reward_type == 14:
            # 暴兵 bb
            self.add_property('bb', training.reward_value)
        elif training.reward_type == 15:
            # 防守 fs
            self.add_property('fs', training.reward_value)
        elif training.reward_type == 16:
            # 运营 yy
            self.add_property('yy', training.reward_value)
        elif training.reward_type == 17:
            # 意识 ys
            self.add_property('ys', training.reward_value)
        elif training.reward_type == 18:
            # 操作 cz
            self.add_property('cz', training.reward_value)
        else:
            raise RuntimeError("Unknown training reward type: {0}".format(training.reward_type))

        self.load_from_db()


    def make_protocol_msg(self):
        msg = ProtocolStaff()
        msg.id = self.id
        msg.oid = self.oid
        msg.level = self.level
        msg.cur_exp = self.exp
        msg.max_exp = 1000
        msg.status = self.status

        for k in StaffProperty.NAME_DICT.keys():
            setattr(msg, k, int(getattr(self, k)))

        for k, v in self.skills:
            msg_skill = msg.skills.add()
            msg_skill.id = k
            msg_skill.level = v

        _in_training = True
        for slot_id, training_id, end_at, is_end in self.get_trainings_info():
            msg_training = msg.training_slots.add()
            if is_end:
                msg_training.status = ProtocolStaff.TrainingSlot.TS_FINISHED
            else:
                if _in_training:
                    msg_training.status = ProtocolStaff.TrainingSlot.TS_TRAINING
                    _in_training = False
                else:
                    msg_training.status = ProtocolStaff.TrainingSlot.TS_QUEUE

            msg_training.slot_id = slot_id
            msg_training.training_id = training_id
            msg_training.end_at = end_at

        for i in range(len(msg.training_slots)):
            if msg.training_slots[i].status == ProtocolStaff.TrainingSlot.TS_QUEUE:
                msg.training_slots[i].end_at += msg.training_slots[i-1].end_at

        # FIXME slot_amount
        slot_amount = 3
        if len(msg.training_slots) < slot_amount:
            for i in range(slot_amount - len(msg.training_slots)):
                msg_training = msg.training_slots.add()
                msg_training.status = ProtocolStaff.TrainingSlot.TS_EMPTY

        return msg


class TrainingInfo(object):
    __slots__ = ['training_id', 'start_at', 'end_at', 'is_end']
    def __init__(self, training_id, start_at):
        self.training_id = training_id
        self.start_at = start_at
        self.end_at = arrow.get(start_at).timestamp + CONFIG.TRAINING[training_id].minutes * 60
        self.is_end = arrow.utcnow().timestamp >= self.end_at
