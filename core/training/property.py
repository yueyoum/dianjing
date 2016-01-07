# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       property
Date Created:   2015-11-02 10:25
Description:    属性训练

"""

import arrow
from dianjing.exception import GameException
from core.mongo import MongoTrainingProperty
from core.staff import StaffManger
from core.package import Property
from core.resource import Resource
from core.item import ItemManager
from core.building import BuildingTrainingCenter
from core.signals import training_property_start_signal, training_property_done_signal

from utils.api import Timerd
from utils.message import MessagePipe
from config import ConfigErrorMessage, ConfigTrainingProperty
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.training_pb2 import (
    TRAINING_SLOT_EMPTY,
    TRAINING_SLOT_FINISH,
    TRAINING_SLOT_TRAINING,
    TRAINING_SLOT_WAITING,

    TrainingPropertyNotify,
)

import formula

PROPERTY_TRAINING_SLOTS_AMOUNT = 4
TIMERD_CALLBACK_PATH = '/api/timerd/training/property/'


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
        # 计算状态
        # 如果没有训练ID，那么就是空，直接返回
        # 有训练ID，要么是训练，要么是完成，要么是等待
        # 这里就是根据 end_at 和 start_at 来判断的
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

        for i in range(PROPERTY_TRAINING_SLOTS_AMOUNT):
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
        for i in range(1, PROPERTY_TRAINING_SLOTS_AMOUNT):
            self.slots[i].start_at = self.slots[i - 1].end_at
            if self.slots[i].status == PropertySlotStatus.TRAINING or self.slots[i].status == PropertySlotStatus.WAITING:
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
        for i in range(PROPERTY_TRAINING_SLOTS_AMOUNT):
            if self.slots[i].status == PropertySlotStatus.EMPTY:
                self.slots[i].training_id = training_id
                if i == 0:
                    # 只有第一个才需要设置start_at
                    self.slots[i].start_at = arrow.utcnow().timestamp
                break
        else:
            raise PropertyTrainingList.ListFull()

        self.calculate()

        # 如果是第一个，就返回第一个的end_at，并且注册定时器
        # 否则其他的只是排队，不注册定时器
        if i == 0:
            return self.slots[i].end_at
        return 0

    def finish(self, slot_id):
        index = slot_id - 1
        slot = self.slots[index]

        if slot.status == PropertySlotStatus.EMPTY:
            raise PropertyTrainingList.SlotEmpty()

        if slot.status == PropertySlotStatus.WAITING:
            raise PropertyTrainingList.SlotWaiting()

        if slot.status == PropertySlotStatus.FINISH:
            raise PropertyTrainingList.SlotFinish()

        slot.end_at = arrow.utcnow().timestamp
        slot.calculate()
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
        if slot_id < 1 or slot_id > PROPERTY_TRAINING_SLOTS_AMOUNT:
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

    def staff_is_training(self, staff_id):
        pl = self.get_training_list(staff_id)
        for i in range(1, PROPERTY_TRAINING_SLOTS_AMOUNT + 1):
            slot = pl.get_slot(i)

            if slot.status != PropertySlotStatus.EMPTY:
                return True

        return False

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

    def update_training_list(self, staff_id, new_list, key=None):
        updater = {'staffs.{0}'.format(staff_id): new_list}

        if key is not None:
            updater['keys.{0}'.format(staff_id)] = key

        MongoTrainingProperty.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_notify(staff_ids=[staff_id])

    def start(self, staff_id, training_id):
        if not StaffManger(self.server_id, self.char_id).has_staff(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        config = ConfigTrainingProperty.get(training_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_NOT_EXIST"))

        building_level = BuildingTrainingCenter(self.server_id, self.char_id).current_level()
        if building_level < config.need_building_level:
            raise GameException(ConfigErrorMessage.get_error_id("BUILDING_TRAINING_CENTER_LEVEL_NOT_ENOUGH"))

        im = ItemManager(self.server_id, self.char_id)
        if not im.check_simple_item_is_enough(config.need_items):
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_ENOUGH"))

        pl = self.get_training_list(staff_id)

        if config.cost_type == 1:
            needs = {'gold': -config.cost_value}
        else:
            needs = {'diamond': -config.cost_value}

        needs['message'] = u"Training Property: {0} for staff {1}".format(training_id, staff_id)

        with Resource(self.server_id, self.char_id).check(**needs):
            try:
                end_at = pl.add(training_id)
            except PropertyTrainingList.ListFull:
                raise GameException(ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_SLOT_FULL"))

            if end_at:
                data = {
                    'sid': self.server_id,
                    'cid': self.char_id,
                    'staff_id': staff_id
                }
                key = Timerd.register(end_at, TIMERD_CALLBACK_PATH, data)
            else:
                key = None

            new_list = pl.get_document_list()
            self.update_training_list(staff_id, new_list, key)

            for item_id, item_amount in config.need_items:
                im.remove_simple_item(item_id, item_amount)

        training_property_start_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            staff_id=staff_id,
        )

    @slot_id_check
    def cancel(self, staff_id, slot_id):
        # 只能取消排队的
        pl = self.get_training_list(staff_id)
        slot = pl.get_slot(slot_id)

        if slot.status != PropertySlotStatus.WAITING:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_CANCEL_NOT_WAITING"))

        pl.remove(slot_id)
        new_list = pl.get_document_list()
        self.update_training_list(staff_id, new_list)

    @slot_id_check
    def speedup(self, staff_id, slot_id):
        pl = self.get_training_list(staff_id)
        slot = pl.get_slot(slot_id)

        try:
            pl.finish(slot_id)
        except PropertyTrainingList.SlotEmpty:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_SPEEDUP_CANNOT_EMPTY"))
        except PropertyTrainingList.SlotWaiting:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_SPEEDUP_CANNOT_WAITING"))
        except PropertyTrainingList.SlotFinish:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_SPEEDUP_CANNOT_FINISH"))

        behind_seconds = slot.end_at - arrow.utcnow().timestamp
        need_diamond = formula.training_speedup_need_diamond(behind_seconds)
        message = u"Training Staff {0} Property Speedup".format(staff_id)

        with Resource(self.server_id, self.char_id).check(diamond=-need_diamond, message=message):
            # 加速后，取消旧定时器，开启新定时器
            doc = MongoTrainingProperty.db(self.server_id).find_one(
                {'_id': self.char_id},
                {'keys.{0}'.format(staff_id): 1}
            )

            key = doc['keys'][str(staff_id)]
            Timerd.cancel(key)

            new_list = pl.get_document_list()
            new_pl = PropertyTrainingList(new_list)

            for i in range(1, PROPERTY_TRAINING_SLOTS_AMOUNT + 1):
                slot = new_pl.get_slot(i)
                if slot.status == PropertySlotStatus.TRAINING:
                    end_at = slot.end_at
                    data = {
                        'sid': self.server_id,
                        'cid': self.char_id,
                        'staff_id': staff_id
                    }
                    new_key = Timerd.register(end_at, TIMERD_CALLBACK_PATH, data)
                    break
            else:
                new_key = ''

            self.update_training_list(staff_id, new_list, new_key)

        training_property_done_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            staff_id=staff_id
        )

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

    def callback(self, staff_id):
        pl = self.get_training_list(staff_id)
        for i in range(1, PROPERTY_TRAINING_SLOTS_AMOUNT + 1):
            slot = pl.get_slot(i)

            if slot.status == PropertySlotStatus.TRAINING:
                pl.finish(i)
                break

        new_list = pl.get_document_list()
        new_pl = PropertyTrainingList(new_list)

        for i in range(1, PROPERTY_TRAINING_SLOTS_AMOUNT + 1):
            slot = new_pl.get_slot(i)
            if slot.status == PropertySlotStatus.TRAINING:
                end_at = slot.end_at
                data = {
                    'sid': self.server_id,
                    'cid': self.char_id,
                    'staff_id': staff_id
                }
                key = Timerd.register(end_at, TIMERD_CALLBACK_PATH, data)
                break
        else:
            key = ''

        self.update_training_list(staff_id, new_list, key)

        training_property_done_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            staff_id=staff_id
        )

    def send_notify(self, staff_ids=None):
        if staff_ids:
            projection = {'staffs.{0}'.format(i): 1 for i in staff_ids}
            act = ACT_UPDATE
        else:
            staff_ids = StaffManger(self.server_id, self.char_id).get_all_staff_ids()
            projection = {'staffs': 1}
            act = ACT_INIT

        doc = MongoTrainingProperty.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

        notify = TrainingPropertyNotify()
        notify.act = act

        for staff_id in staff_ids:
            training_list = doc['staffs'].get(str(staff_id), [])

            notify_staff = notify.staffs.add()
            notify_staff.staff_id = staff_id

            pl = PropertyTrainingList(training_list)

            # 每个人有 PROPERTY_TRAINING_SLOTS_AMOUNT 个训练位
            for i in range(1, PROPERTY_TRAINING_SLOTS_AMOUNT + 1):
                notify_staff_training = notify_staff.trainings.add()
                notify_staff_training.slot_id = i

                slot = pl.get_slot(i)
                if slot.status == PropertySlotStatus.EMPTY:
                    notify_staff_training.status = TRAINING_SLOT_EMPTY
                elif slot.status == PropertySlotStatus.FINISH:
                    notify_staff_training.status = TRAINING_SLOT_FINISH
                elif slot.status == PropertySlotStatus.TRAINING:
                    notify_staff_training.status = TRAINING_SLOT_TRAINING
                else:
                    notify_staff_training.status = TRAINING_SLOT_WAITING

                notify_staff_training.training_id = slot.training_id
                notify_staff_training.end_at = slot.end_at

        MessagePipe(self.char_id).put(msg=notify)
