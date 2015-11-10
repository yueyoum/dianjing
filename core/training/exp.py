# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       exp
Date Created:   2015-11-02 10:25
Description:    经验训练

"""

import arrow
from dianjing.exception import GameException
from core.mongo import MongoTrainingExp
from core.staff import StaffManger
from core.building import BuildingTrainingCenter
from core.package import Property
from core.resource import Resource
from utils.message import MessagePipe
from utils.api import Timerd

from config import ConfigErrorMessage, ConfigBuilding
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.training_pb2 import (
    TRAINING_SLOT_EMPTY,
    TRAINING_SLOT_TRAINING,
    TRAINING_SLOT_NOT_OPEN,
    TRAINING_SLOT_FINISH,

    TrainingExpSlotNotify,
)

import formula

EXP_TRAINING_TOTAL_SECONDS = 8 * 3600  # 8 hours
TIMERD_CALLBACK_PATH = '/api/timerd/training/exp/'


def current_got_exp(passed_seconds, current_building_level):
    config_building_level = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).get_level(current_building_level)
    return passed_seconds / 60 * config_building_level.value1


class ExpSlotStatus(object):
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

        self.status = ExpSlotStatus.EMPTY
        self.staff_id = 0
        self.start_at = 0
        self.end_at = 0
        self.exp = -1
        self.key = ''

    @property
    def finished(self):
        return self.exp > -1

    @property
    def current_exp(self):
        if self.finished:
            return self.exp

        passed_seconds = arrow.utcnow().timestamp - self.start_at
        return current_got_exp(passed_seconds, self.current_building_level)

    def _check_slot_id(self):
        max_building_level = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).max_levels
        max_slots_amount = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).get_level(max_building_level).value2
        if self.slot_id > max_slots_amount:
            self.status = ExpSlotStatus.NOT_EXIST
            return False

        current_slots_amount = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).get_level(
            self.current_building_level).value2
        if self.slot_id > current_slots_amount:
            self.status = ExpSlotStatus.NOT_OPEN
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

        doc = MongoTrainingExp.db(self.server_id).find_one(
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
        self.exp = data['exp']
        self.key = data['key']

        if self.finished:
            self.status = ExpSlotStatus.FINISH
        else:
            self.status = ExpSlotStatus.TRAINING
            self.end_at = self.start_at + EXP_TRAINING_TOTAL_SECONDS


class TrainingExp(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoTrainingExp.exist(self.server_id, self.char_id):
            doc = MongoTrainingExp.document()
            doc['_id'] = self.char_id
            MongoTrainingExp.db(self.server_id).insert_one(doc)

    def staff_is_training(self, staff_id):
        doc = MongoTrainingExp.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'slots': 1}
        )

        for slot in doc['slots'].values():
            if slot.get('staff_id', 0) == staff_id:
                return True

        return False

    def open_slots_by_building_level_up(self):
        current_level = BuildingTrainingCenter(self.server_id, self.char_id).get_level()
        old_level = current_level - 1

        current_slot_amount = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).get_level(current_level).value2
        old_slot_amount = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).get_level(old_level).value2

        if current_slot_amount <= old_slot_amount:
            return

        notify = TrainingExpSlotNotify()
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

        :rtype : ExpSlotStatus
        """
        current_building_level = BuildingTrainingCenter(self.server_id, self.char_id).get_level()
        slot = ExpSlotStatus(self.server_id, self.char_id, slot_id, current_building_level)
        slot.load_data()

        if slot.status == ExpSlotStatus.NOT_EXIST:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_NOT_EXIST"))

        if slot.status == ExpSlotStatus.NOT_OPEN:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_NOT_OPEN"))

        return slot

    def start(self, slot_id, staff_id):
        from core.training import TrainingBroadcast, TrainingShop

        staff = StaffManger(self.server_id, self.char_id).get_staff(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        slot = self.get_slot(slot_id)

        if slot.status != ExpSlotStatus.EMPTY:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_IN_USE"))

        # 不能同时进行
        if TrainingBroadcast(self.server_id, self.char_id).staff_is_training(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_DOING_BROADCAST"))

        if TrainingShop(self.server_id, self.char_id).staff_is_training(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_DOING_SHOP"))

        doc = MongoTrainingExp.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'slots': 1}
        )

        for k, v in doc['slots'].iteritems():
            if v.get('staff_id', 0) == staff_id:
                raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_STAFF_IN_TRAINING"))

        need_gold = formula.staff_training_exp_need_gold(staff.level)
        message = u"Training Exp For Staff {0}".format(staff_id)

        with Resource(self.server_id, self.char_id).check(gold=-need_gold, message=message):
            timestamp = arrow.utcnow().timestamp

            end_at = timestamp + EXP_TRAINING_TOTAL_SECONDS
            data = {
                'sid': self.server_id,
                'cid': self.char_id,
                'slot_id': slot_id
            }

            key = Timerd.register(end_at, TIMERD_CALLBACK_PATH, data)

            training_doc = MongoTrainingExp.document_training()
            training_doc['staff_id'] = staff_id
            training_doc['start_at'] = timestamp
            training_doc['exp'] = -1
            training_doc['key'] = key

            MongoTrainingExp.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'slots.{0}'.format(slot_id): training_doc
                }}
            )

        self.send_notify(slot_ids=[slot_id])

    def cancel(self, slot_id):
        slot = self.get_slot(slot_id)

        if slot.status == ExpSlotStatus.EMPTY:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_EMPTY"))

        if slot.status == ExpSlotStatus.FINISH:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_FINISH_CANNOT_OPERATE"))

        Timerd.cancel(slot.key)

        p = Property()
        p.staff_exp = slot.current_exp
        adds = p.to_dict()

        StaffManger(self.server_id, self.char_id).update(slot.staff_id, **adds)
        self.clean(slot_id)

        return p.make_protomsg()

    def speedup(self, slot_id):
        slot = self.get_slot(slot_id)

        if slot.status == ExpSlotStatus.EMPTY:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_EMPTY"))

        if slot.status == ExpSlotStatus.FINISH:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_FINISH_CANNOT_OPERATE"))

        behind_seconds = slot.end_at - arrow.utcnow().timestamp
        need_diamond = formula.training_speedup_need_diamond(behind_seconds)
        message = u"Training Exp Speedup."
        with Resource(self.server_id, self.char_id).check(diamond=-need_diamond, message=message):
            Timerd.cancel(slot.key)

            current_building_level = BuildingTrainingCenter(self.server_id, self.char_id).get_level()
            exp = current_got_exp(EXP_TRAINING_TOTAL_SECONDS, current_building_level)

            MongoTrainingExp.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'slots.{0}.exp'.format(slot_id): exp,
                    'slots.{0}.key'.format(slot_id): ''
                }}
            )

        self.send_notify(slot_ids=[slot_id])

    def callback(self, slot_id):
        slot = self.get_slot(slot_id)
        if slot.status != ExpSlotStatus.TRAINING:
            return 0

        end_at = slot.end_at
        if end_at > arrow.utcnow().timestamp:
            return end_at

        current_building_level = BuildingTrainingCenter(self.server_id, self.char_id).get_level()
        exp = current_got_exp(EXP_TRAINING_TOTAL_SECONDS, current_building_level)

        MongoTrainingExp.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'slots.{0}.exp'.format(slot_id): exp,
                'slots.{0}.key'.format(slot_id): ''
            }}
        )

        self.send_notify(slot_ids=[slot_id])
        return 0

    def get_reward(self, slot_id):
        slot = self.get_slot(slot_id)

        if slot.status != ExpSlotStatus.FINISH:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_NOT_FINISH"))

        p = Property()
        p.staff_exp = slot.current_exp
        adds = p.to_dict()

        StaffManger(self.server_id, self.char_id).update(slot.staff_id, **adds)
        self.clean(slot_id)
        return p.make_protomsg()

    def clean(self, slot_id):
        MongoTrainingExp.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'slots.{0}'.format(slot_id): {}
            }}
        )

        self.send_notify(slot_ids=[slot_id])

    def send_notify(self, slot_ids=None):
        building_max_level = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).max_levels
        max_slot_amount = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).get_level(building_max_level).value2

        current_building_level = BuildingTrainingCenter(self.server_id, self.char_id).get_level()

        if slot_ids:
            projection = {'slots.{0}'.format(i): 1 for i in slot_ids}
            act = ACT_UPDATE
        else:
            projection = {'slots': 1}
            act = ACT_INIT
            slot_ids = range(1, max_slot_amount + 1)

        doc = MongoTrainingExp.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

        slots_data = doc['slots']

        notify = TrainingExpSlotNotify()
        notify.act = act

        for i in slot_ids:
            notify_slot = notify.slots.add()
            notify_slot.id = i

            slot = ExpSlotStatus(self.server_id, self.char_id, i, current_building_level)
            slot.parse_data(slots_data)

            if slot.status == ExpSlotStatus.NOT_EXIST:
                raise RuntimeError("Exp slot {0} not exist".format(i))

            if slot.status == ExpSlotStatus.NOT_OPEN:
                notify_slot.status = TRAINING_SLOT_NOT_OPEN
            elif slot.status == ExpSlotStatus.TRAINING:
                notify_slot.status = TRAINING_SLOT_TRAINING
            elif slot.status == ExpSlotStatus.FINISH:
                notify_slot.status = TRAINING_SLOT_FINISH
            else:
                notify_slot.status = TRAINING_SLOT_EMPTY

            if slot.staff_id:
                notify_slot.staff.id = slot.staff_id
                notify_slot.staff.got_exp = slot.current_exp
                notify_slot.staff.end_at = slot.end_at

        MessagePipe(self.char_id).put(msg=notify)
