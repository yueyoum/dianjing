# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       core
Date Created:   2015-04-28 15:15
Description:

"""

import json
import arrow

from dianjing.exception import GameException

from apps.staff.models import Staff as ModelStaff, StaffTraining as ModelStaffTraining
from apps.staff.property import StaffProperty
from utils.message import MessagePipe

from protomsg.staff_pb2 import Staff as ProtocolStaff
from protomsg.staff_pb2 import StaffNotify, StaffRemoveNotify
from protomsg.common_pb2 import ACT_ADD, ACT_INIT, ACT_UPDATE

from config import CONFIG



class StaffManager(object):
    def __init__(self, char_id):
        self.char_id = char_id


    def add(self, oid, send_notify=True):
        if oid not in CONFIG.STAFF:
            raise GameException( CONFIG.ERRORMSG["STAFF_NOT_EXIST"].id )

        try:
            s = ModelStaff.objects.create(
                char_id=self.char_id,
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


    def training(self, staff_id, training_id):
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
        # trainings = [(id, end_at, is_end)]
        trainings = []
        for tr in ModelStaffTraining.objects.filter(staff_id=self.id).order_by('start_at'):
            end_at = arrow.get(tr.start_at).timestamp + CONFIG.TRAINING[tr.training_id].minutes * 60
            is_end = arrow.utcnow().timestamp >= end_at

            trainings.append(
                (tr.training_id, end_at, is_end)
            )

        return trainings


    def make_protocol_msg(self):
        msg = ProtocolStaff()
        msg.id = self.id
        msg.oid = self.oid
        msg.level = self.level
        msg.cur_exp = self.exp
        msg.max_exp = 1000
        msg.status = self.status

        for k in StaffProperty.NAME_DICT.keys():
            setattr(msg, k, getattr(self, k))

        for k, v in self.skills:
            msg_skill = msg.skills.add()
            msg_skill.id = k
            msg_skill.level = v

        for tid, end_at, _ in self.get_trainings_info():
            msg_training = msg.training_queue.add()
            msg_training.id = tid
            msg_training.end_at = end_at

        return msg

