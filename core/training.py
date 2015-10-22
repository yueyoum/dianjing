# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training
Date Created:   2015-07-21 15:45
Description:

"""
import arrow

from dianjing.exception import GameException

from core.mongo import MongoTrainingExp, MongoTrainingProperty
from core.staff import StaffManger, staff_level_up_need_exp
from core.building import BuildingTrainingCenter
from core.package import Property
from core.resource import Resource
from core.bag import BagItem

from utils.message import MessagePipe

from config import ConfigErrorMessage, ConfigBuilding, ConfigTrainingProperty

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.training_pb2 import TrainingExpSlotNotify, TrainingPropertyNotify

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
        p.staff_exp = exp
        return p.make_protomsg()

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
        p.staff_exp = exp
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


class PropertySlotStatus(object):
    # 属性训练槽位是按照顺序初始化的
    # 因为同时只能有一个在训练中，排在后面的处于等待状态
    EMPTY = 1
    TRAINING = 2
    WAITING = 3
    FINISH = 4

    @classmethod
    def empty(cls):
        return cls(0, {})

    def __init__(self, start_at, slot_data):
        self.start_at = start_at
        self.training_id = slot_data.get('id', 0)
        self.end_at = slot_data.get('end_at', 0)
        self.status = PropertySlotStatus.EMPTY
        self.speedup = False

        self.calculate()

    def __str__(self):
        if self.status == PropertySlotStatus.EMPTY:
            return "<EMPTY>"

        if self.status == PropertySlotStatus.TRAINING:
            return "<TRAINING>"

        if self.status == PropertySlotStatus.WAITING:
            return "<WAITING>"

        if self.status == PropertySlotStatus.FINISH:
            return "<FINISH>"

    def calculate(self):
        if not self.training_id:
            self.status = PropertySlotStatus.EMPTY
            return

        if not self.end_at:
            self.end_at = self.start_at + ConfigTrainingProperty.get(self.training_id).minutes * 60

        timestamp = arrow.utcnow().timestamp
        if timestamp >= self.end_at:
            self.status = PropertySlotStatus.FINISH
        elif timestamp >= self.start_at:
            self.status = PropertySlotStatus.TRAINING
        else:
            self.status = PropertySlotStatus.WAITING

    def to_document(self):
        return {
            'id': self.training_id,
            'end_at': self.end_at
        }


class PropertyTrainingList(object):
    class ListFull(Exception):
        pass

    class SlotEmpty(Exception):
        pass

    class SlotFinish(Exception):
        pass

    class SlotWaiting(Exception):
        pass

    def __init__(self, training_list):
        # training_list 是存在数据库中的数据
        # 格式 [{'id': training_id, 'end_at': timestamp}, ...]
        self.training_list = training_list
        self.slots = []

        for i in range(4):
            try:
                data = self.training_list[i]
            except IndexError:
                data = {}

            if i == 0:
                start_at = 0
            else:
                start_at = self.slots[i - 1].end_at

            slot = PropertySlotStatus(start_at, data)
            self.slots.append(slot)

    def __str__(self):
        slot_str_list = [str(slot) for slot in self.slots]
        return "[{0}]".format(", ".join(slot_str_list))

    def calculate(self):
        self.slots[0].calculate()
        for i in range(1, 4):
            self.slots[i].start_at = self.slots[i - 1].end_at
            if not self.slots[i].speedup:
                # 如果是加速完成的，就不能清空end_at
                # 否则就要清空end_at，让其重新计算
                self.slots[i].end_at = 0
            self.slots[i].calculate()

    def get_slot(self, slot_id):
        # slot_id 就是index，只不过是从1开始的
        """

        :rtype : PropertySlotStatus
        """
        return self.slots[slot_id - 1]

    def get_document_list(self):
        return [slot.to_document() for slot in self.slots]

    def add(self, training_id):
        if self.slots[0].status == PropertySlotStatus.EMPTY:
            # 这个员工没有训练
            self.slots[0].training_id = training_id
            self.slots[0].start_at = arrow.utcnow().timestamp
        else:
            for i in range(1, 4):
                if self.slots[i].status == PropertySlotStatus.EMPTY:
                    self.slots[i].training_id = training_id
                    self.slots[i].start_at = self.slots[i - 1].end_at
                    break
            else:
                raise PropertyTrainingList.ListFull()

        self.calculate()

    def finish(self, slot_id):
        index = slot_id - 1
        slot = self.slots[index]

        if slot.status == PropertySlotStatus.EMPTY:
            raise PropertyTrainingList.SlotEmpty()

        if slot.status == PropertySlotStatus.WAITING:
            raise PropertyTrainingList.SlotWaiting()

        if slot.status == PropertySlotStatus.FINISH:
            raise PropertyTrainingList.SlotFinish()

        slot.speedup = True
        slot.end_at = arrow.utcnow().timestamp

        self.calculate()

    def remove(self, slot_id):
        index = slot_id - 1
        slot = self.slots[index]

        if index < 3:
            if slot.status == PropertySlotStatus.TRAINING:
                self.slots[index + 1].start_at = arrow.utcnow().timestamp
            elif slot.status == PropertySlotStatus.FINISH:
                self.slots[index + 1].start_at = slot.end_at

        self.slots.pop(index)
        self.slots.append(PropertySlotStatus.empty())

        self.calculate()


def slot_id_check(func):
    def deco(self, staff_id, slot_id):
        """

        :type self : TrainingProperty
        """
        if slot_id < 1 or slot_id > 4:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_SLOT_NOT_EXIST"))

        return func(self, staff_id, slot_id)

    return deco


class TrainingProperty(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoTrainingProperty.exist(self.server_id, self.char_id):
            doc = MongoTrainingProperty.document()
            doc['_id'] = self.char_id
            MongoTrainingProperty.db(self.server_id).insert_one(doc)

    def get_training_list(self, staff_id):
        """

        :rtype : PropertyTrainingList
        """
        doc = MongoTrainingProperty.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'staffs.{0}'.format(staff_id): 1}
        )

        training_list = doc['staffs'].get(str(staff_id), [])
        return PropertyTrainingList(training_list)

    def update_training_list(self, staff_id, new_list):
        MongoTrainingProperty.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'staffs.{0}'.format(staff_id): new_list
            }}
        )

        self.send_notify(staff_ids=[staff_id])

    def start(self, staff_id, training_id):
        if not StaffManger(self.server_id, self.char_id).has_staff(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        config = ConfigTrainingProperty.get(training_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_NOT_EXIST"))

        bag = BagItem(self.server_id, self.char_id)
        if not bag.has(config.need_items):
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_ENOUGH"))

        pl = self.get_training_list(staff_id)

        try:
            pl.add(training_id)
        except PropertyTrainingList.ListFull:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_SLOT_FULL"))

        new_list = pl.get_document_list()
        self.update_training_list(staff_id, new_list)

    @slot_id_check
    def cancel(self, staff_id, slot_id):
        pl = self.get_training_list(staff_id)
        slot = pl.get_slot(slot_id)

        if slot.status == PropertySlotStatus.EMPTY:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_CANCEL_CANNOT_EMPTY"))

        if slot.status == PropertySlotStatus.TRAINING:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_CANCEL_CANNOT_TRAINING"))

        if slot.status == PropertySlotStatus.FINISH:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_CANCEL_CANNOT_FINISH"))

        pl.remove(slot_id)
        new_list = pl.get_document_list()
        self.update_training_list(staff_id, new_list)

    @slot_id_check
    def speedup(self, staff_id, slot_id):
        pl = self.get_training_list(staff_id)
        slot = pl.get_slot(slot_id)

        behind_seconds = slot.end_at - arrow.utcnow().timestamp
        minutes, seconds = divmod(behind_seconds, 60)
        if seconds:
            minutes += 1

        need_diamond = minutes * 10
        message = u"Training Staff {0} Property Speedup, Minutes {0}".format(staff_id, minutes)

        with Resource(self.server_id, self.char_id).check(diamond=-need_diamond, message=message):
            try:
                pl.finish(slot_id)
            except PropertyTrainingList.SlotEmpty:
                raise GameException(ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_SPEEDUP_CANNOT_EMPTY"))
            except PropertyTrainingList.SlotWaiting:
                raise GameException(ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_SPEEDUP_CANNOT_WAITING"))
            except PropertyTrainingList.SlotFinish:
                raise GameException(ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_SPEEDUP_CANNOT_FINISH"))

            new_list = pl.get_document_list()
            self.update_training_list(staff_id, new_list)

    @slot_id_check
    def get_reward(self, staff_id, slot_id):
        pl = self.get_training_list(staff_id)
        slot = pl.get_slot(slot_id)

        if slot.status != PropertySlotStatus.FINISH:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_REWARD_CANNOT"))

        training_id = slot.training_id

        p = Property.generate(ConfigTrainingProperty.get(training_id).package)
        adds = p.to_dict()
        StaffManger(self.server_id, self.char_id).update(staff_id, **adds)

        pl.remove(slot_id)
        new_list = pl.get_document_list()
        self.update_training_list(staff_id, new_list)

        return p.make_protomsg()

    def send_notify(self, staff_ids=None):
        if staff_ids:
            projection = {'staffs.{0}'.format(i): 1 for i in staff_ids}
            act = ACT_UPDATE
        else:
            projection = {'staffs': 1}
            act = ACT_INIT

        doc = MongoTrainingProperty.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

        notify = TrainingPropertyNotify()
        notify.act = act

        for staff_id, training_list in doc['staffs'].iteritems():
            notify_staff = notify.staffs.add()
            notify_staff.staff_id = int(staff_id)

            pl = PropertyTrainingList(training_list)

            # 每个人有4个训练位
            for i in range(1, 5):
                notify_staff_training = notify_staff.trainings.add()
                notify_staff_training.slot_id = i

                slot = pl.get_slot(i)
                notify_staff_training.training_id = slot.training_id
                notify_staff_training.end_at = slot.end_at

        MessagePipe(self.char_id).put(msg=notify)
