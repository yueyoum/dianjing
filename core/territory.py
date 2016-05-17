# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       territory
Date Created:   2016-05-16 10-02
Description:

"""

import arrow

from dianjing.exception import GameException

from core.mongo import MongoTerritory
from core.times_log import TimesLogTerritoryBuildingInspireTimes
from core.staff import StaffManger

from utils.message import MessagePipe

from config import ConfigErrorMessage, ConfigTerritoryBuilding, ConfigInspireCost, ConfigItemNew

from protomsg.territory_pb2 import (
    TerritoryNotify,
    TerritoryBuilding as MsgBuilding,
    TerritorySlot as MsgSlot,
    TERRITORY_BUILDING_OPEN,
    TERRITORY_BUILDING_LOCK,
    TERRITORY_SLOT_OPEN,
    TERRITORY_SLOT_LOCK,
)

from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT

# TODO
INIT_TERRITORY_BUILDING_IDS = [1, 2, 3]
TRAINING_HOURS = [4, 8, 12]
BUILDING_PRODUCT_ID_TABLE = {
    1: 30012,
    2: 30013,
    3: 30014,
}


class Slot(object):
    def __init__(self, building_id, slot_id, data):
        self.id = slot_id
        self.building_id = building_id
        self.product_id = BUILDING_PRODUCT_ID_TABLE[building_id]
        if data:
            self.open = True
            self.staff_id = data['staff_id']
            self.start_at = data['start_at']
            self.hour = data['hour']
            self.report = data['report']
            self.reward = data['reward']
            self.end_at = self.start_at + self.hour * 3600
        else:
            self.open = False

    @classmethod
    def parse_key(cls, key):
        building_id, slot_id, staff_id, hour = key.split(':')
        return int(building_id), int(slot_id), int(staff_id), int(hour)

    @property
    def key(self):
        if not self.open:
            return ""

        return "{0}:{1}:{2}:{3}".format(self.building_id, self.id, self.staff_id, self.hour)

    @property
    def finished(self):
        return self.end_at >= arrow.utcnow().timestamp

    def reward_building_exp(self):
        # TODO
        return 10

    def reward_product_amount(self):
        # TODO
        return 20

    def make_protomsg(self):
        msg = MsgSlot()
        msg.id = self.id
        if self.open:
            msg.status = TERRITORY_SLOT_OPEN
            msg.staff_id = self.staff_id
            msg.hour = self.hour
            msg.end_at = self.end_at
            msg.key = self.key
            for _id, _args, _timestamp in self.report:
                msg_report = msg.report.add()
                msg_report.id = _id
                msg_report.param.extend(_args)
                msg_report.timestamp = _timestamp
        else:
            msg.status = TERRITORY_SLOT_LOCK

        return msg


class Building(object):
    def __init__(self, server_id, char_id, building_id, data, slot_ids=None):
        self.server_id = server_id
        self.char_id = char_id

        self.id = building_id
        self.product_id = BUILDING_PRODUCT_ID_TABLE[building_id]
        if data:
            self.open = True
            self.level = data['level']
            self.exp = data['exp']
            self.product_amount = data['product_amount']

            self.slots = {}
            """:type: dict[int, Slot]"""

            if not slot_ids:
                slot_ids = ConfigTerritoryBuilding.get(self.id).slots.keys()
            for slot_id in slot_ids:
                slot_data = data['slots'].get(str(slot_id), None)
                self.slots[slot_id] = Slot(self.id, slot_id, slot_data)
        else:
            self.open = False

    def current_inspire_times(self):
        if not self.open:
            return 0
        return TimesLogTerritoryBuildingInspireTimes(self.server_id, self.char_id).count_of_today(sub_id=self.id)

    def remained_inspire_times(self):
        if not self.open:
            return 0

        return ConfigTerritoryBuilding.get(self.id).levels[self.level].inspire.max_times - self.current_inspire_times()

    def inspire_cost(self):
        if not self.open:
            return 0

        times = self.current_inspire_times() + 1
        return ConfigInspireCost.get(times)

    def make_protomsg(self):
        msg = MsgBuilding()
        msg.id = self.id
        msg.product_id = self.product_id

        if self.open:
            msg.status = TERRITORY_BUILDING_OPEN
            msg.level = self.level
            msg.exp = self.exp
            msg.product_amount = self.product_amount
            msg.inspire_cost = self.inspire_cost()
            msg.remained_inspire_times = self.remained_inspire_times()

            for _, s in self.slots.iteritems():
                msg_slot = msg.slots.add()
                msg_slot.MergeFrom(s.make_protomsg())
        else:
            msg.status = TERRITORY_BUILDING_LOCK

        return msg


class Territory(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.doc = MongoTerritory.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoTerritory.document()
            self.doc['_id'] = self.char_id
            # TODO
            self.doc['work_card'] = 5000

            for i in INIT_TERRITORY_BUILDING_IDS:
                building_doc = MongoTerritory.document_building()
                building_config = ConfigTerritoryBuilding.get(i)

                for slot_id, slot_config in building_config.slots.iteritems():
                    if slot_config.need_building_level < 1:
                        # TODO VIP check
                        building_doc['slots'][str(slot_id)] = MongoTerritory.document_slot()

                self.doc['buildings'][str(i)] = building_doc

            MongoTerritory.db(self.server_id).insert_one(self.doc)

    def training_check(self, building_id, slot_id, staff_id, hour):
        if hour not in TRAINING_HOURS:
            raise GameException(ConfigErrorMessage.get_error_id('BAD_MESSAGE'))

        StaffManger(self.server_id, self.char_id).check_staff([staff_id])

        try:
            b_data = self.doc['buildings'][str(building_id)]
        except KeyError:
            raise GameException(ConfigErrorMessage.get_error_id("TERRITORY_BUILDING_LOCK"))

        building = Building(self.server_id, self.char_id, building_id, b_data)
        try:
            slot = building.slots[slot_id]
        except KeyError:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if not slot.open:
            raise GameException(ConfigErrorMessage.get_error_id("TERRITORY_SLOT_LOCK"))

        if slot.staff_id:
            raise GameException(ConfigErrorMessage.get_error_id("TERRITORY_SLOT_HAS_STAFF"))

        # TODO check whether this staff is in training

        return slot

    def training_prepare(self, building_id, slot_id, staff_id, hour):
        slot = self.training_check(building_id, slot_id, staff_id, hour)

        slot.staff_id = staff_id
        slot.hour = hour

        return slot

    def training_star(self, key):
        try:
            building_id, slot_id, staff_id, hour = Slot.parse_key(key)
        except:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        building_level = Building(self.server_id, self.char_id, building_id, self.doc['buildings'][str(building_id)]).level

        config_slot = ConfigTerritoryBuilding.get(building_id).slots[slot_id]
        cost_amount = config_slot.get_cost_amount(building_level, TRAINING_HOURS.index(hour))

        if cost_amount > self.doc['work_card']:
            raise GameException(ConfigErrorMessage.get_error_id("TERRITORY_WORK_CARD_NOT_ENOUGH"))

        self.doc['work_card'] -= cost_amount

        slot = self.training_check(building_id, slot_id, staff_id, hour)
        slot.staff_id = staff_id
        slot.hour = hour

        start_at = arrow.utcnow().timestamp

        slot_doc = MongoTerritory.document_slot()
        slot_doc['staff_id'] = staff_id
        slot_doc['start_at'] = start_at
        slot_doc['hour'] = hour

        # 固定奖励
        report = [
            (
                1,
                [str(slot.reward_building_exp()), ConfigItemNew.get(slot.product_id).name,
                 str(slot.reward_product_amount())],
                start_at
            ),
        ]

        # 选手特产

        # 概率奖励

        end_at = start_at + hour * 3600
        extra_at = start_at + 1800
        while extra_at < end_at:
            # TODO building_level
            _item_id, _item_amount = ConfigTerritoryBuilding.get(building_id).slots[slot_id].get_extra_product(1)

            report.append((
                3,
                [ConfigItemNew.get(_item_id).name, str(_item_amount)],
                extra_at
            ))

            extra_at += 1800

        slot_doc['report'] = report

        self.doc['buildings'][str(building_id)]['slots'][str(slot_id)] = slot_doc
        MongoTerritory.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'work_card': self.doc['work_card'],
                'buildings.{0}.slots.{1}'.format(building_id, slot_id): slot_doc
            }}
        )

        self.send_notify(building_id=building_id, slot_id=slot_id)

    def training_get_reward(self, key):
        pass

    def send_notify(self, building_id=None, slot_id=None):
        # building_id 和 slot_id 都没有: 全部同步
        # 有building_id，没有 slot_id:  同步整个这个building
        # 有building_id, 也有slot_id: 只同步这个building中的这个slot
        # 没有building_id, 有slot_id: 这是错误情况

        bid_sid_map = {}

        def _get_sids_of_bid(_bid):
            if _bid in bid_sid_map:
                return [bid_sid_map[_bid]]

            return ConfigTerritoryBuilding.get(_bid).slots.keys()

        if building_id:
            act = ACT_UPDATE
            bids = [building_id]
            if slot_id:
                bid_sid_map[building_id] = slot_id

        else:
            if slot_id:
                raise RuntimeError("Territory send_notify, no building_id, but has slot_id")

            act = ACT_INIT
            bids = ConfigTerritoryBuilding.INSTANCES.keys()

        notify = TerritoryNotify()
        notify.act = act
        notify.training_hours.extend(TRAINING_HOURS)
        notify.work_card = self.doc['work_card']

        for bid in bids:
            b_data = self.doc['buildings'].get(str(bid), None)
            b_obj = Building(self.server_id, self.char_id, bid, b_data, slot_ids=_get_sids_of_bid(bid))

            notify_building = notify.buildings.add()
            notify_building.MergeFrom(b_obj.make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)
