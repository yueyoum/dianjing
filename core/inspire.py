# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       inspire
Date Created:   2016-10-28 11:18
Description:

"""
from dianjing.exception import GameException

from core.mongo import MongoInspire

from core.challenge import Challenge
from core.staff import StaffManger
from core import checker
from core.signals import inspire_staff_changed_signal

from utils.message import MessagePipe

from config import ConfigErrorMessage, ConfigInspire, ConfigInspireAddition

from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT
from protomsg.inspire_pb2 import (
    INSPIRE_SLOT_EMPTY,
    INSPIRE_SLOT_LOCK,
    INSPIRE_SLOT_USING,

    InspireNotify
)


class Inspire(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.doc = MongoInspire.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoInspire.document()
            self.doc['_id'] = self.char_id
            MongoInspire.db(self.server_id).insert_one(self.doc)

        self.try_open_slots(send_notify=False)

    def try_open_slots(self, send_notify=True):
        opened = []
        updater = {}

        c = Challenge(self.server_id, self.char_id)
        for challenge_id, slot_id in ConfigInspire.LIST:
            if not c.is_challenge_id_passed(challenge_id):
                continue

            if str(slot_id) in self.doc['slots']:
                continue

            self.doc['slots'][str(slot_id)] = 0
            opened.append(slot_id)
            updater['slots.{0}'.format(slot_id)] = 0

        if updater:
            MongoInspire.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': updater}
            )

        if send_notify and opened:
            self.send_notify(opened)

    def is_staff_in(self, staff_id):
        for k, v in self.doc['slots'].iteritems():
            if v == staff_id:
                return True

        return False

    def check_staff_in(self, staff_id):
        if self.is_staff_in(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("INSPIRE_STAFF_IN"))

    def all_staffs(self):
        staffs = []
        for k, v in self.doc['slots'].iteritems():
            if v:
                staffs.append(v)

        return staffs

    def set_staff(self, slot_id, staff_id):
        slot_id = str(slot_id)

        if slot_id not in self.doc['slots']:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        updater = {}

        if not staff_id:
            # 下人
            if not self.doc['slots'][slot_id]:
                raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

            self.doc['slots'][slot_id] = ""
            updater['slots.{0}'.format(slot_id)] = ""
        else:
            # 上人
            checker.staff_exists(self.server_id, self.char_id, staff_id)
            checker.staff_not_in_formation(self.server_id, self.char_id, staff_id)

            self.check_staff_in(staff_id)

            self.doc['slots'][slot_id] = staff_id
            updater['slots.{0}'.format(slot_id)] = staff_id

        MongoInspire.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_notify(ids=[int(slot_id)])

        inspire_staff_changed_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            staff_id=staff_id
        )

    def get_addition_config(self):
        sm = StaffManger(self.server_id, self.char_id)
        # XXX 不能用 get_staff_object
        all_staffs = sm.get_staffs_data()

        levels = 0
        steps = 0

        for s in self.all_staffs():
            data = all_staffs[s]
            levels += data['level']
            steps += data['step']

        config_level_addition = ConfigInspireAddition.get_by_level(levels)
        config_step_addition = ConfigInspireAddition.get_by_step(steps)

        return config_level_addition, config_step_addition

    def send_notify(self, ids=None):
        if ids:
            act = ACT_UPDATE
        else:
            ids = ConfigInspire.INSTANCES.keys()
            act = ACT_INIT

        notify = InspireNotify()
        notify.act = act

        for i in ids:
            notify_slot = notify.slots.add()
            notify_slot.id = i

            staff_id = self.doc['slots'].get(str(i), None)
            if staff_id is None:
                notify_slot.status = INSPIRE_SLOT_LOCK
            else:
                if staff_id:
                    notify_slot.status = INSPIRE_SLOT_USING
                    notify_slot.staff_id = staff_id
                else:
                    notify_slot.status = INSPIRE_SLOT_EMPTY

        MessagePipe(self.char_id).put(msg=notify)
