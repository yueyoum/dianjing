# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       broadcast
Date Created:   2015-11-02 10:26
Description:    直播训练

"""

import arrow

from dianjing.exception import GameException

from core.mongo import MongoTrainingBroadcast
from core.staff import StaffManger
from core.building import BuildingBusinessCenter
from core.package import Drop
from core.resource import Resource

from utils.api import Timerd
from utils.message import MessagePipe

from config import ConfigErrorMessage, ConfigBuilding

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.training_pb2 import (
    TRAINING_SLOT_EMPTY,
    TRAINING_SLOT_FINISH,
    TRAINING_SLOT_NOT_OPEN,
    TRAINING_SLOT_TRAINING,

    TrainingBroadcastNotify,
)

import formula

# 直播
BROADCAST_TOTAL_SECONDS = 8 * 3600
TIMERD_CALLBACK_PATH = '/api/timerd/training/broadcast/'


def current_got_gold(passed_seconds, current_building_level):
    config_building_level = ConfigBuilding.get(BuildingBusinessCenter.BUILDING_ID).get_level(current_building_level)
    gold = passed_seconds / 60 * config_building_level.value1
    # TODO 技能加成，知名度加成
    return gold


class BroadcastSlotStatus(object):
    NOT_EXIST = 1
    NOT_OPEN = 2
    EMPTY = 3
    TRAINING = 4
    FINISH = 5

    def __init__(self, server_id, char_id, slot_id, current_building_level):
        self.server_id = server_id
        self.char_id = char_id
        self.slot_id = slot_id
        self.current_building_level = current_building_level

        self.status = BroadcastSlotStatus.EMPTY
        self.staff_id = 0
        self.start_at = 0
        self.end_at = 0
        self.gold = -1
        self.key = ''

    @property
    def finished(self):
        return self.gold > -1

    @property
    def current_gold(self):
        if self.finished:
            return self.gold

        passed_seconds = arrow.utcnow().timestamp - self.start_at
        return current_got_gold(passed_seconds, self.current_building_level)

    def _check_slot_id(self):
        max_building_level = ConfigBuilding.get(BuildingBusinessCenter.BUILDING_ID).max_levels
        max_slots_amount = ConfigBuilding.get(BuildingBusinessCenter.BUILDING_ID).get_level(max_building_level).value2
        if self.slot_id > max_slots_amount:
            self.status = BroadcastSlotStatus.NOT_EXIST
            return False

        current_slots_amount = ConfigBuilding.get(BuildingBusinessCenter.BUILDING_ID).get_level(
            self.current_building_level).value2
        if self.slot_id > current_slots_amount:
            self.status = BroadcastSlotStatus.NOT_OPEN
            return False

        return True

    def parse_data(self, slots_data):
        check_result = self._check_slot_id()
        if not check_result:
            return

        data = slots_data.get(str(self.slot_id), {})
        self._calculate(data)

    def load_data(self):
        check_result = self._check_slot_id()
        if not check_result:
            return

        doc = MongoTrainingBroadcast.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'slots.{0}'.format(self.slot_id): 1}
        )

        data = doc['slots'].get(str(self.slot_id), {})
        self._calculate(data)

    def _calculate(self, data):
        if not data:
            return

        self.staff_id = data['staff_id']
        if not self.staff_id:
            return

        self.start_at = data['start_at']
        self.gold = data['gold']
        self.key = data['key']

        if self.finished:
            self.status = BroadcastSlotStatus.FINISH
        else:
            self.status = BroadcastSlotStatus.TRAINING
            self.end_at = self.start_at + BROADCAST_TOTAL_SECONDS


class TrainingBroadcast(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoTrainingBroadcast.exist(self.server_id, self.char_id):
            doc = MongoTrainingBroadcast.document()
            doc['_id'] = self.char_id
            MongoTrainingBroadcast.db(self.server_id).insert_one(doc)

    def open_slots_by_building_level_up(self):
        current_level = BuildingBusinessCenter(self.server_id, self.char_id).get_level()
        old_level = current_level - 1

        current_slot_amount = ConfigBuilding.get(BuildingBusinessCenter.BUILDING_ID).get_level(current_level).value2
        old_slot_amount = ConfigBuilding.get(BuildingBusinessCenter.BUILDING_ID).get_level(old_level).value2

        if current_slot_amount <= old_slot_amount:
            return

        notify = TrainingBroadcastNotify()
        notify.act = ACT_UPDATE

        for i in range(1, current_slot_amount + 1):
            if i <= old_slot_amount:
                continue

            notify_slot = notify.slots.add()
            notify_slot.id = i
            notify_slot.status = TRAINING_SLOT_EMPTY

        MessagePipe(self.char_id).put(msg=notify)

    def get_slot(self, slot_id):
        """

        :rtype : BroadcastSlotStatus
        """
        current_building_level = BuildingBusinessCenter(self.server_id, self.char_id).get_level()
        slot = BroadcastSlotStatus(self.server_id, self.char_id, slot_id, current_building_level)
        slot.load_data()

        if slot.status == BroadcastSlotStatus.NOT_EXIST:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_BROADCAST_SLOT_NOT_EXIST"))

        if slot.status == BroadcastSlotStatus.NOT_OPEN:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_BROADCAST_SLOT_NOT_OPEN"))

        return slot

    def start(self, slot_id, staff_id):
        if not StaffManger(self.server_id, self.char_id).has_staff(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        slot = self.get_slot(slot_id)
        if slot.status != BroadcastSlotStatus.EMPTY:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_BROADCAST_NOT_EMPTY"))

        doc = MongoTrainingBroadcast.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'slots': 1}
        )

        for _, v in doc['slots'].iteritems():
            if v and v.get('staff_id', 0) == staff_id:
                raise GameException(ConfigErrorMessage.get_error_id("TRAINING_BROADCAST_STAFF_IN_TRAINING"))

        timestamp = arrow.utcnow().timestamp
        end_at = timestamp + BROADCAST_TOTAL_SECONDS
        data = {
            'sid': self.server_id,
            'cid': self.char_id,
            'slot_id': slot_id
        }

        key = Timerd.register(end_at, TIMERD_CALLBACK_PATH, data)

        slot_doc = MongoTrainingBroadcast.document_slot()
        slot_doc['staff_id'] = staff_id
        slot_doc['start_at'] = arrow.utcnow().timestamp
        slot_doc['gold'] = -1
        slot_doc['key'] = key

        MongoTrainingBroadcast.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'slots.{0}'.format(slot_id): slot_doc
            }}
        )

        self.send_notify(slot_ids=[slot_id])

    def cancel(self, slot_id):
        slot = self.get_slot(slot_id)
        if slot.status != BroadcastSlotStatus.TRAINING:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_BROADCAST_NOT_TRAINING"))

        drop = Drop()
        drop.gold = slot.current_gold
        message = u"Broadcast Training Cancel For Staff {0}".format(slot.staff_id)
        Resource(self.server_id, self.char_id).save_drop(drop, message)

        Timerd.cancel(slot.key)

        MongoTrainingBroadcast.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'slots.{0}'.format(slot_id): {}
            }}
        )

        self.send_notify(slot_ids=[slot_id])
        return drop.make_protomsg()

    def speedup(self, slot_id):
        slot = self.get_slot(slot_id)
        if slot.status != BroadcastSlotStatus.TRAINING:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_BROADCAST_NOT_TRAINING"))

        behind_seconds = slot.end_at - arrow.utcnow().timestamp
        need_diamond = formula.training_speedup_need_diamond(behind_seconds)
        message = u"Training Broadcast Speedup."

        with Resource(self.server_id, self.char_id).check(diamond=-need_diamond, message=message):
            Timerd.cancel(slot.key)

            current_building_level = BuildingBusinessCenter(self.server_id, self.char_id).get_level()
            gold = current_got_gold(BROADCAST_TOTAL_SECONDS, current_building_level)

            MongoTrainingBroadcast.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'slots.{0}.gold'.format(slot_id): gold,
                    'slots.{0}.key'.format(slot_id): ''
                }}
            )

        self.send_notify(slot_ids=[slot_id])

    def callback(self, slot_id):
        slot = self.get_slot(slot_id)
        if slot.status != BroadcastSlotStatus.TRAINING:
            return 0

        end_at = slot.end_at
        if end_at > arrow.utcnow().timestamp:
            return end_at

        current_building_level = BuildingBusinessCenter(self.server_id, self.char_id).get_level()
        gold = current_got_gold(BROADCAST_TOTAL_SECONDS, current_building_level)

        MongoTrainingBroadcast.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'slots.{0}.gold'.format(slot_id): gold,
                'slots.{0}.key'.format(slot_id): ''
            }}
        )

        self.send_notify(slot_ids=[slot_id])

    def get_reward(self, slot_id):
        slot = self.get_slot(slot_id)
        if slot.status != BroadcastSlotStatus.FINISH:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_BROADCAST_NOT_FINISH"))

        drop = Drop()
        drop.gold = slot.current_gold
        message = u"Broadcast Training Get Reward For Staff {0}".format(slot.staff_id)
        Resource(self.server_id, self.char_id).save_drop(drop, message)

        MongoTrainingBroadcast.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'slots.{0}'.format(slot_id): {}
            }}
        )

        self.send_notify(slot_ids=[slot_id])
        return drop.make_protomsg()

    def send_notify(self, slot_ids=None):
        building_max_level = ConfigBuilding.get(BuildingBusinessCenter.BUILDING_ID).max_levels
        max_slot_amount = ConfigBuilding.get(BuildingBusinessCenter.BUILDING_ID).get_level(building_max_level).value2

        current_building_level = BuildingBusinessCenter(self.server_id, self.char_id).get_level()

        if slot_ids:
            act = ACT_UPDATE
            projection = {'slots.{0}'.format(i): 1 for i in slot_ids}
        else:
            act = ACT_INIT
            projection = {'slots': 1}
            slot_ids = range(1, max_slot_amount + 1)

        doc = MongoTrainingBroadcast.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

        slots_data = doc['slots']

        notify = TrainingBroadcastNotify()
        notify.act = act

        for i in slot_ids:
            notify_slot = notify.slots.add()
            notify_slot.id = i

            slot = BroadcastSlotStatus(self.server_id, self.char_id, i, current_building_level)
            slot.parse_data(slots_data)

            if slot.status == BroadcastSlotStatus.NOT_EXIST:
                raise RuntimeError("Broadcast slot {0} not exist".format(i))

            if slot.status == BroadcastSlotStatus.NOT_OPEN:
                notify_slot.status = TRAINING_SLOT_NOT_OPEN
            elif slot.status == BroadcastSlotStatus.TRAINING:
                notify_slot.status = TRAINING_SLOT_TRAINING
            elif slot.status == BroadcastSlotStatus.FINISH:
                notify_slot.status = TRAINING_SLOT_FINISH
            else:
                notify_slot.status = TRAINING_SLOT_EMPTY

            if slot.staff_id:
                notify_slot.staff.id = slot.staff_id
                notify_slot.staff.got_gold = slot.current_gold
                notify_slot.staff.end_at = slot.end_at

        MessagePipe(self.char_id).put(msg=notify)
