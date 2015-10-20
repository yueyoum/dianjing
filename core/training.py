# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training
Date Created:   2015-07-21 15:45
Description:

"""
import arrow

from dianjing.exception import GameException

from core.mongo import MongoTrainingExp
from core.staff import StaffManger, staff_level_up_need_exp
from core.building import BuildingTrainingCenter
from core.resource import Resource

from utils.message import MessagePipe

from config import ConfigErrorMessage, ConfigBuilding

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.training_pb2 import TrainingExpSlotNotify
from protomsg.package_pb2 import Property

TOTAL_SECONDS = 8 * 3600  # 8 hours


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
        self.speedup = False
        self.time_point = 0
        self.exp = 0

    @property
    def finished(self):
        if self.speedup:
            return True

        return arrow.utcnow().timestamp >= self.end_at

    @property
    def current_exp(self):
        if self.finished:
            return self.exp

        new_exp = self.calculate_new_exp()
        return self.exp + new_exp

    def calculate_new_exp(self, end_at=None):
        # 计算上个time_point到当前增加的经验
        if not end_at:
            end_at = arrow.utcnow().timestamp

        last_time_point = self.time_point if self.time_point else self.start_at

        config_building_level = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).get_level(
            self.current_building_level)
        new_exp = (end_at - last_time_point) / 60 * config_building_level.value1
        return new_exp

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
        self.end_at = data['start_at'] + TOTAL_SECONDS
        self.speedup = data['speedup']
        self.time_point = data['time_point']
        self.exp = data['exp']

        if self.finished:
            self.status = ExpSlotStatus.FINISH
        else:
            self.status = ExpSlotStatus.TRAINING


class TrainingExp(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.current_building_level = BuildingTrainingCenter(self.server_id, self.char_id).get_level()

        if not MongoTrainingExp.exist(self.server_id, self.char_id):
            doc = MongoTrainingExp.document()
            doc['_id'] = self.char_id
            MongoTrainingExp.db(self.server_id).insert_one(doc)

    def get_slot_status(self, slot_id):
        """

        :rtype : ExpSlotStatus
        """
        return ExpSlotStatus(self.server_id, self.char_id, slot_id, self.current_building_level)

    def start(self, slot_id, staff_id):
        staff = StaffManger(self.server_id, self.char_id).get_staff(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        ss = self.get_slot_status(slot_id)
        ss.load_data()

        if ss.status == ExpSlotStatus.NOT_EXIST:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_NOT_EXIST"))

        if ss.status == ExpSlotStatus.NOT_OPEN:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_NOT_OPEN"))

        if ss.status != ExpSlotStatus.EMPTY:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_IN_USE"))

        doc = MongoTrainingExp.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'slots': 1}
        )

        for k, v in doc['slots'].iteritems():
            if v.get('staff_id', 0) == staff_id:
                raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_STAFF_IN_TRAINING"))

        timestamp = arrow.utcnow().timestamp
        training_doc = MongoTrainingExp.document_training()
        training_doc['staff_id'] = staff_id
        training_doc['start_at'] = timestamp
        training_doc['time_point'] = timestamp
        training_doc['exp'] = 0
        training_doc['speedup'] = False

        need_gold = staff_level_up_need_exp(staff_id, staff['level'])
        message = u"Training Exp For Staff {0}".format(staff_id)

        with Resource(self.server_id, self.char_id).check(gold=-need_gold, message=message):
            MongoTrainingExp.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'slots.{0}'.format(slot_id): training_doc
                }}
            )

            self.send_notify(slot_ids=[slot_id])

    def cancel(self, slot_id):
        ss = self.get_slot_status(slot_id)
        ss.load_data()

        if ss.status == ExpSlotStatus.NOT_EXIST:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_NOT_EXIST"))

        if ss.status == ExpSlotStatus.NOT_OPEN:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_NOT_OPEN"))

        if ss.status == ExpSlotStatus.EMPTY:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_EMPTY"))

        if ss.status == ExpSlotStatus.FINISH:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_FINISH_CANNOT_OPERATE"))

        staff_id = ss.staff_id
        exp = ss.current_exp

        # TODO 优化
        StaffManger(self.server_id, self.char_id).update(staff_id, exp=exp)
        
        self.clean(slot_id)

        p = Property()
        p_exp = p.resources.add()
        p_exp.resource_id = 'staff_exp'
        p_exp.value = exp
        return p

    def speedup(self, slot_id):
        ss = self.get_slot_status(slot_id)
        ss.load_data()

        if ss.status == ExpSlotStatus.NOT_EXIST:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_NOT_EXIST"))

        if ss.status == ExpSlotStatus.NOT_OPEN:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_NOT_OPEN"))

        if ss.status == ExpSlotStatus.EMPTY:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_EMPTY"))

        if ss.status == ExpSlotStatus.FINISH:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_FINISH_CANNOT_OPERATE"))

        behind_seconds = ss.end_at - arrow.utcnow().timestamp
        minutes, seconds = divmod(behind_seconds, 60)
        if seconds:
            minutes += 1

        need_diamond = minutes * 10
        message = u"Training Exp Speedup."
        with Resource(self.server_id, self.char_id).check(diamond=-need_diamond, message=message):
            new_exp = ss.calculate_new_exp(end_at=ss.end_at)
            exp = ss.exp + new_exp

            MongoTrainingExp.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'slots.{0}.exp'.format(slot_id): exp,
                    'slots.{0}.speedup'.format(slot_id): True
                }}
            )

            self.send_notify(slot_ids=[slot_id])

    def get_reward(self, slot_id):
        ss = self.get_slot_status(slot_id)
        ss.load_data()

        if ss.status == ExpSlotStatus.NOT_EXIST:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_NOT_EXIST"))

        if ss.status == ExpSlotStatus.NOT_OPEN:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_NOT_OPEN"))

        if ss.status != ExpSlotStatus.FINISH:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_EXP_NOT_FINISH"))

        exp = ss.current_exp

        # TODO
        StaffManger(self.server_id, self.char_id).update(ss.staff_id, exp=exp)

        self.clean(slot_id)

        p = Property()
        p_exp = p.resources.add()
        p_exp.resource_id = 'staff_exp'
        p_exp.value = exp
        return p


    def clean(self, slot_id):
        MongoTrainingExp.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'slots.{0}'.format(slot_id): {}
            }}
        )

        self.send_notify(slot_ids=[slot_id])


    def send_notify(self, slot_ids=None):
        if slot_ids:
            projection = {'slots.{0}'.format(i): 1 for i in slot_ids}
            act = ACT_UPDATE
        else:
            projection = {'slots': 1}
            act = ACT_INIT

        slots_amount = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).get_level(
            self.current_building_level).value2

        doc = MongoTrainingExp.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

        slots_data = doc['slots']

        notify = TrainingExpSlotNotify()
        notify.act = act

        for i in range(1, slots_amount + 1):
            if act == ACT_UPDATE and i not in slot_ids:
                continue

            notify_slot = notify.slots.add()
            notify_slot.id = i

            ss = self.get_slot_status(i)
            ss.parse_data(slots_data)

            if ss.status == ExpSlotStatus.NOT_OPEN or ss.status == ExpSlotStatus.NOT_EXIST:
                raise RuntimeError("exp slot error: status = {0}".format(ss.status))

            if ss.status == ExpSlotStatus.EMPTY:
                continue

            notify_slot.staff.id = ss.staff_id
            notify_slot.staff.got_exp = ss.current_exp

            if ss.status == ExpSlotStatus.FINISH:
                notify_slot.staff.end_at = -1
            else:
                notify_slot.staff.end_at = ss.end_at

        MessagePipe(self.char_id).put(msg=notify)
