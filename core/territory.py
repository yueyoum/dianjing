# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       territory
Date Created:   2016-05-16 10-02
Description:

"""
import math
import random

import arrow

from dianjing.exception import GameException

from core.mongo import MongoTerritory
from core.value_log import (
    ValueLogTerritoryBuildingInspireTimes,
    ValueLogTerritoryStoreBuyTimes,
    ValueLogTerritoryHelpFriendTimes,
    ValueLogTerritoryTrainingTimes,
)

from core.club import Club
from core.staff import StaffManger
from core.friend import FriendManager
from core.resource import ResourceClassification, TERRITORY_PRODUCT_BUILDING_TABLE
from core.match import ClubMatch

from utils.message import MessagePipe

from config import (
    ConfigErrorMessage,
    ConfigTerritoryBuilding,
    ConfigInspireCost,
    ConfigItemNew,
    ConfigTerritoryStaffProduct,
    ConfigTerritoryStore,
    ConfigTerritoryEvent,
    ConfigNPCFormation,
)

from protomsg.territory_pb2 import (
    TerritoryNotify,
    TerritoryBuilding as MsgBuilding,
    TerritorySlot as MsgSlot,
    TERRITORY_BUILDING_OPEN,
    TERRITORY_BUILDING_LOCK,
    TERRITORY_SLOT_OPEN,
    TERRITORY_SLOT_LOCK,

    TerritoryStoreNotify,
)

from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT

# TODO
INIT_TERRITORY_BUILDING_IDS = [101, 102, 103]
TRAINING_HOURS = [4, 8, 12]
BUILDING_PRODUCT_ID_TABLE = {v: k for k, v in TERRITORY_PRODUCT_BUILDING_TABLE.iteritems()}

STAFF_QUALITY_MODULUS = {
    1: 0.5,
    2: 0.6,
    3: 0.7,
    4: 0.8,
    5: 0.9,
}

# TODO real time
# 事件发生间隔分钟数
EVENT_INTERVAL = {
    1: [5, 6],
    2: [3, 5],
    3: [2, 3],
}


class ResultItems(object):
    __slots__ = ['items']

    def __init__(self):
        self.items = {}

    def add(self, _id, _amount):
        if _id not in self.items:
            self.items[_id] = _amount
        else:
            self.items[_id] += _amount


class Slot(object):
    __slots__ = [
        'server_id', 'char_id', 'id', 'building_id', 'building_level', 'product_id',
        'open', 'staff_id', 'start_at', 'hour', 'report', 'reward', 'end_at'
    ]

    def __init__(self, server_id, char_id, building_id, building_level, slot_id, data):
        self.server_id = server_id
        self.char_id = char_id

        self.id = slot_id
        self.building_id = building_id
        self.building_level = building_level
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

    @property
    def finished(self):
        if not self.staff_id:
            return False

        return arrow.utcnow().timestamp >= self.end_at

    def get_building_reward(self):
        if not self.open:
            return 0, 0

        if not self.staff_id:
            return 0, 0

        staff_obj = StaffManger(self.server_id, self.char_id).get_staff_object(self.staff_id)

        quality_modulus = STAFF_QUALITY_MODULUS[ConfigItemNew.get(staff_obj.oid).quality]
        slot_modulus = ConfigTerritoryBuilding.get(self.building_id).slots[self.id].exp_modulus
        exp = (100 * math.pow(self.building_level, 0.9) +
               100 * math.pow(self.hour, 0.5)) * quality_modulus * slot_modulus
        product_amount = (150 * math.pow(self.building_level, 0.8) +
                          150 * math.pow(self.hour, 0.6)) * quality_modulus * slot_modulus

        return int(exp), int(product_amount)

    def make_protomsg(self):
        msg = MsgSlot()
        msg.id = self.id
        if self.open:
            msg.status = TERRITORY_SLOT_OPEN
            msg.staff_id = self.staff_id
            msg.hour = self.hour
            msg.end_at = self.end_at
            for _id, _args, _timestamp in self.report:
                msg_report = msg.report.add()
                msg_report.id = _id
                msg_report.param.extend(_args)
                msg_report.timestamp = _timestamp
        else:
            msg.status = TERRITORY_SLOT_LOCK

        return msg


class Building(object):
    __slots__ = [
        'server_id', 'char_id', 'id', 'product_id',
        'open', 'level', 'exp', 'product_amount',
        'slots',
        'event_id', 'event_at',
    ]

    def __init__(self, server_id, char_id, building_id, data, slot_ids=None):
        self.server_id = server_id
        self.char_id = char_id

        self.id = building_id
        self.product_id = BUILDING_PRODUCT_ID_TABLE[building_id]

        self.event_id = 0

        if data:
            self.open = True
            self.level = data['level']
            self.exp = data['exp']
            self.product_amount = data['product_amount']

            self.event_id = data.get('event_id', 0)
            self.event_at = data.get('event_at', 0)

            self.slots = {}
            """:type: dict[int, Slot]"""

            if slot_ids is None:
                slot_ids = ConfigTerritoryBuilding.get(self.id).slots.keys()
            for slot_id in slot_ids:
                slot_data = data['slots'].get(str(slot_id), None)
                self.slots[slot_id] = Slot(self.server_id, self.char_id, self.id, self.level, slot_id, slot_data)
        else:
            self.open = False

    def add_exp(self, exp):
        config = ConfigTerritoryBuilding.get(self.id)
        max_level = max(config.levels.keys())

        self.exp += exp
        while True:
            if self.level >= max_level:
                self.level = max_level
                if self.exp >= config.levels[max_level].exp:
                    self.exp = config.levels[max_level].exp - 1

                break

            update_need_exp = config.levels[self.level].exp
            if self.exp < update_need_exp:
                break

            self.exp -= update_need_exp
            self.level += 1

    def add_product(self, amount):
        self.product_amount += amount

        limit = ConfigTerritoryBuilding.get(self.id).levels[self.level].product_limit
        if self.product_amount >= limit:
            self.product_amount = limit

    def current_inspire_times(self):
        if not self.open:
            return 0
        return ValueLogTerritoryBuildingInspireTimes(self.server_id, self.char_id).count_of_today(sub_id=self.id)

    def remained_inspire_times(self):
        if not self.open:
            return 0

        return ConfigTerritoryBuilding.get(self.id).levels[self.level].inspire.max_times - self.current_inspire_times()

    def inspire_cost(self):
        if not self.open:
            return 0

        times = self.current_inspire_times() + 1
        return ConfigInspireCost.get(times)

    def get_working_slot_amount(self):
        working_slot_amount = 0
        for _, s in self.slots.iteritems():
            if s.open and s.staff_id:
                working_slot_amount += 1

        return working_slot_amount

    def refresh_event_id(self):
        if not self.open:
            return

        # working_amount = self.get_working_slot_amount()
        # try:
        #     i1, i2 = EVENT_INTERVAL[working_amount]
        # except KeyError:
        #     return

        # interval = random.randint(i1, i2)
        interval = 2
        now = arrow.utcnow().timestamp
        if self.event_at + interval > now:
            return

        event_id = random.choice(ConfigTerritoryBuilding.get(self.id).levels[self.level].events)
        self.event_id = event_id
        self.event_at = now

        # NOTE 这里自己存盘
        MongoTerritory.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'buildings.{0}.event_id'.format(self.id): self.event_id,
                'buildings.{0}.event_at'.format(self.id): self.event_at,
            }}
        )

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

    def check_product(self, items):
        # items: [(_id, amount),]
        for _id, amount in items:
            building_id = TERRITORY_PRODUCT_BUILDING_TABLE[_id]
            if self.doc['buildings'][str(building_id)]['product_amount'] < amount:
                raise GameException(ConfigErrorMessage.get_error_id("ITEM_{0}_NOT_ENOUGH".format(_id)))

    def remove_product(self, items):
        # items: [(_id, amount),]
        updater = {}

        for _id, amount in items:
            building_id = TERRITORY_PRODUCT_BUILDING_TABLE[_id]

            new_amount = self.doc['buildings'][str(building_id)]['product_amount'] - amount
            if new_amount < 0:
                new_amount = 0

            self.doc['buildings'][str(building_id)]['product_amount'] = new_amount
            updater['buildings.{0}.product_amount'.format(building_id)] = new_amount

        MongoTerritory.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_notify()

    def add_product(self, items):
        # items: [(_id, amount),]
        updater = {}

        for _id, amount in items:
            building_id = TERRITORY_PRODUCT_BUILDING_TABLE[_id]

            building = self.get_building_object(building_id, slots_ids=[])
            building.add_product(amount)

            self.doc['buildings'][str(building_id)]['product_amount'] = building.product_amount
            updater['buildings.{0}.product_amount'.format(building_id)] = building.product_amount

        MongoTerritory.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_notify()


    def add_work_card(self, amount):
        self.doc['work_card'] += amount
        self.send_notify(building_id=[], slot_id=[])

    def check_work_card(self, amount):
        new_amount = self.doc['work_card'] - amount
        if new_amount < 0:
            raise GameException(ConfigErrorMessage.get_error_id("TERRITORY_WORK_CARD_NOT_ENOUGH"))

        return new_amount

    def remove_work_card(self, amount):
        new_amount = self.check_work_card(amount)
        self.doc['work_card'] = new_amount

        MongoTerritory.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'work_card': self.doc['work_card'],
            }}
        )

        self.send_notify(building_id=[], slot_id=[])

    def get_all_building_objects(self):
        """

        :rtype: dict[int, Building]
        """
        objects = {}
        for k, v in self.doc['buildings'].iteritems():
            objects[int(k)] = Building(self.server_id, self.char_id, int(k), v)

        return objects

    def get_building_object(self, bid, slots_ids=None):
        """

        :rtype: Building
        """
        try:
            b_data = self.doc['buildings'][str(bid)]
        except KeyError:
            raise GameException(ConfigErrorMessage.get_error_id("TERRITORY_BUILDING_LOCK"))

        return Building(self.server_id, self.char_id, bid, b_data, slot_ids=slots_ids)

    def training_star(self, building_id, slot_id, staff_id, hour):
        if hour not in TRAINING_HOURS:
            raise GameException(ConfigErrorMessage.get_error_id('BAD_MESSAGE'))

        sm = StaffManger(self.server_id, self.char_id)
        sm.check_staff([staff_id])

        building = self.get_building_object(building_id, slots_ids=[slot_id])
        try:
            slot = building.slots[slot_id]
        except KeyError:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if not slot.open:
            raise GameException(ConfigErrorMessage.get_error_id("TERRITORY_SLOT_LOCK"))

        if slot.staff_id:
            raise GameException(ConfigErrorMessage.get_error_id("TERRITORY_SLOT_HAS_STAFF"))

        # TODO check whether this staff is in training
        building_level = self.get_building_object(building_id, slots_ids=[]).level

        config_slot = ConfigTerritoryBuilding.get(building_id).slots[slot_id]
        cost_amount = config_slot.get_cost_amount(building_level, TRAINING_HOURS.index(hour))

        new_amount = self.check_work_card(cost_amount)
        self.doc['work_card'] = new_amount

        slot.staff_id = staff_id
        slot.hour = hour

        start_at = arrow.utcnow().timestamp

        slot_doc = MongoTerritory.document_slot()
        slot_doc['staff_id'] = staff_id
        slot_doc['start_at'] = start_at
        slot_doc['hour'] = hour

        building_exp, product_amount = slot.get_building_reward()
        reward = {
            'building_exp': building_exp,
            'product_amount': product_amount,
            'items': []
        }

        ri = ResultItems()

        # 固定奖励
        report = [
            (
                1,
                [str(building_exp), ConfigItemNew.get(slot.product_id).name,
                 str(product_amount)],
                start_at
            ),
        ]

        # 选手特产
        config_staff_product = ConfigTerritoryStaffProduct.get(sm.get_staff_object(staff_id).oid)
        if config_staff_product:
            _id, _amount = config_staff_product.get_product(TRAINING_HOURS.index(hour))

            report.append((
                2,
                [ConfigItemNew.get(_id).name, str(_amount)],
                start_at + 600
            ))

            ri.add(_id, _amount)

        # 概率奖励
        end_at = start_at + hour * 3600
        extra_at = start_at + 1800
        while extra_at < end_at:
            # TODO building_level
            _id, _amount = ConfigTerritoryBuilding.get(building_id).slots[slot_id].get_extra_product(1)

            report.append((
                3,
                [ConfigItemNew.get(_id).name, str(_amount)],
                extra_at
            ))

            ri.add(_id, _amount)
            extra_at += 1800

        reward['items'] = ri.items.items()

        slot_doc['report'] = report
        slot_doc['reward'] = reward

        self.doc['buildings'][str(building_id)]['slots'][str(slot_id)] = slot_doc
        MongoTerritory.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'work_card': self.doc['work_card'],
                'buildings.{0}.slots.{1}'.format(building_id, slot_id): slot_doc
            }}
        )

        ValueLogTerritoryTrainingTimes(self.server_id, self.char_id).record()

        self.send_notify(building_id=building_id, slot_id=slot_id)

    def training_get_reward(self, building_id, slot_id):
        building = self.get_building_object(building_id, slots_ids=[slot_id])
        try:
            slot = building.slots[slot_id]
        except KeyError:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if not slot.open:
            raise GameException(ConfigErrorMessage.get_error_id("TERRITORY_SLOT_LOCK"))

        if not slot.finished:
            raise GameException(ConfigErrorMessage.get_error_id("TERRITORY_SLOT_NOT_FINISH"))

        reward = slot.reward

        building.add_exp(reward['building_exp'])
        building.add_product(reward['product_amount'])

        empty_slot_doc = MongoTerritory.document_slot()

        self.doc['buildings'][str(building_id)]['level'] = building.level
        self.doc['buildings'][str(building_id)]['exp'] = building.exp
        self.doc['buildings'][str(building_id)]['product_amount'] = building.product_amount
        self.doc['buildings'][str(building_id)]['slots'][str(slot_id)] = empty_slot_doc

        MongoTerritory.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'buildings.{0}.level'.format(building_id): building.level,
                'buildings.{0}.exp'.format(building_id): building.exp,
                'buildings.{0}.product_amount'.format(building_id): building.product_amount,
                'buildings.{0}.slots.{1}'.format(building_id, slot_id): empty_slot_doc
            }}
        )

        self.send_notify(building_id=building_id, slot_id=slot_id)

        resource_classified = ResourceClassification.classify(reward['items'])
        resource_classified.add(self.server_id, self.char_id)

        # 把建筑产出也要发回到客户端
        resource_classified.bag.append((BUILDING_PRODUCT_ID_TABLE[building_id], reward['product_amount']))
        return resource_classified

    def add_building_exp(self, building_id, exp):
        building = self.get_building_object(building_id, slots_ids=[])
        building.add_exp(exp)

        # TODO 格子解锁
        MongoTerritory.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'buildings.{0}.level'.format(building_id): building.level,
                'buildings.{0}.exp'.format(building_id): building.exp,
            }}
        )
        self.send_notify(building_id=building_id)

    def send_notify(self, building_id=None, slot_id=None):
        # building_id 和 slot_id 都没有: 全部同步
        # 有building_id，没有 slot_id:  同步整个这个building
        # 有building_id, 也有slot_id: 只同步这个building中的这个slot
        # 没有building_id, 有slot_id: 这是错误情况
        # building_id 和 slot_id 都是 []: 只同步其他信息

        bid_sid_map = {}

        def _get_sids_of_bid(_bid):
            if _bid in bid_sid_map:
                return [bid_sid_map[_bid]]

            return ConfigTerritoryBuilding.get(_bid).slots.keys()

        if building_id is None:
            if slot_id:
                raise RuntimeError("Territory send_notify, no building_id, but has slot_id")

            act = ACT_INIT
            bids = ConfigTerritoryBuilding.INSTANCES.keys()
        else:
            act = ACT_UPDATE
            if building_id:
                bids = [building_id]
                if slot_id:
                    bid_sid_map[building_id] = slot_id
            else:
                bids = []

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


class TerritoryStore(object):
    __slots__ = ['server_id', 'char_id', 'times']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.times = ValueLogTerritoryStoreBuyTimes(self.server_id, self.char_id).batch_count_of_today()

    def get_remained_times(self, _id):
        t = self.times.get(str(_id), 0)
        max_times = ConfigTerritoryStore.get(_id).max_times

        remained = max_times - t
        if remained < 0:
            remained = 0

        return remained

    def buy(self, item_id):
        config = ConfigTerritoryStore.get(item_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("TERRITORY_STORE_ITEM_NOT_EXIST"))

        remained_times = self.get_remained_times(item_id)
        if not remained_times:
            raise GameException(ConfigErrorMessage.get_error_id("TERRITORY_STORE_ITEM_NO_TIMES"))

        resource_classified = ResourceClassification.classify(config.needs)
        resource_classified.check_exist(self.server_id, self.char_id)
        resource_classified.remove(self.server_id, self.char_id)

        got = [(config.item_id, config.item_amount), ]
        resource_classified = ResourceClassification.classify(got)
        resource_classified.add(self.server_id, self.char_id)

        if str(item_id) in self.times:
            self.times[str(item_id)] += 1
        else:
            self.times[str(item_id)] = 1

        ValueLogTerritoryStoreBuyTimes(self.server_id, self.char_id).record(sub_id=item_id)

        self.send_notify(item_id=item_id)
        return resource_classified

    def send_notify(self, item_id=None):
        if item_id:
            act = ACT_UPDATE
            item_ids = [item_id]
        else:
            act = ACT_INIT
            item_ids = ConfigTerritoryStore.INSTANCES.keys()

        notify = TerritoryStoreNotify()
        notify.act = act
        for i in item_ids:
            notify_item = notify.items.add()
            notify_item.id = i
            notify_item.remained_times = self.get_remained_times(i)

        MessagePipe(self.char_id).put(msg=notify)


class TerritoryFriend(object):
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def get_list(self):
        friend_ids = FriendManager(self.server_id, self.char_id).get_real_friends_ids()
        info = {}
        """:type: dict[int, list[dict]]"""

        for fid in friend_ids:
            t = Territory(self.server_id, self.char_id)
            buildings = t.get_all_building_objects()

            b_list = []
            for _, b_obj in buildings.iteritems():
                b_obj.refresh_event_id()

                b_list.append({
                    'id': b_obj.id,
                    'level': b_obj.level,
                    'event_id': b_obj.event_id
                })

            info[fid] = b_list
        return info

    def help(self, friend_id, building_id):
        friend_id = int(friend_id)

        if not FriendManager(self.server_id, self.char_id).check_friend_exist(friend_id):
            raise GameException(ConfigErrorMessage.get_error_id("FRIEND_NOT_OK"))

        t = Territory(self.server_id, self.char_id)
        building = t.get_building_object(building_id, slots_ids=[])

        event_id = building.event_id

        if not event_id:
            raise GameException(ConfigErrorMessage.get_error_id("TERRITORY_BUILDING_NO_EVENT"))

        MongoTerritory.db(self.server_id).update_one(
            {'_id': friend_id},
            {'$set': {
                'buildings.{0}.event_id': 0
            }}
        )

        ValueLogTerritoryHelpFriendTimes(self.server_id, self.char_id).record()

        config = ConfigTerritoryEvent.get(event_id)
        if not config.npc:
            resource_classified = ResourceClassification.classify(config.reward_win)
            resource_classified.add(self.server_id, friend_id)

            Territory(self.server_id, friend_id).add_building_exp(building_id, config.target_exp)
            return None, resource_classified

        npc_club = ConfigNPCFormation.get(config.npc)
        my_club = Club(self.server_id, self.char_id)

        match = ClubMatch(my_club, npc_club)
        msg = match.start()
        msg.key = "{0}:{1}:{2}".format(friend_id, building_id, event_id)
        return msg, None

    def match_report(self, key, win):
        try:
            friend_id, building_id, event_id = key.split(':')
            friend_id = int(friend_id)
            building_id = int(building_id)
            event_id = int(event_id)
        except:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        config = ConfigTerritoryEvent.get(event_id)
        Territory(self.server_id, friend_id).add_building_exp(building_id, config.target_exp)

        if win:
            drop = config.reward_win
        else:
            drop = config.reward_lose

        resource_classified = ResourceClassification.classify(drop)
        resource_classified.add(self.server_id, self.char_id)
        return resource_classified
