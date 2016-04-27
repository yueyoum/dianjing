# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       bag
Date Created:   2016-03-10 10-37
Description:

"""
from dianjing.exception import GameException

from core.mongo import MongoBag
from core.club import Club, get_club_property
from core.resource import MONEY, ResourceClassification, money_text_to_item_id

from utils.functional import make_string_id
from utils.message import MessagePipe

from config import (
    ConfigErrorMessage,
    ConfigItemNew,
    ConfigEquipmentNew,
    ConfigItemUse,
    ConfigItemMerge,
    GlobalConfig,
)

from config.settings import (
    BAG_EQUIPMENT_MAX_AMOUNT,
    BAG_FRAGMENT_MAX_AMOUNT,
    BAG_STUFF_MAX_AMOUNT,
)

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.bag_pb2 import (
    BagSlotsNotify,
    BagSlotsRemoveNotify,
    Equipment as MsgEquipment,
)

TYPE_ITEM_NORMAL = 1  # 普通道具
TYPE_ITEM_CAN_USE = 2  # 可使用道具
TYPE_MONEY = 3  # 代币 -- 不会进包裹
TYPE_EQUIPMENT = 4  # 装备
TYPE_FRAGMENT = 5  # 碎片
TYPE_STAFF = 6  # 选手 -- 不会进包裹

BAG_CAN_CONTAINS_TYPE = [
    TYPE_ITEM_NORMAL,
    TYPE_ITEM_CAN_USE,
    TYPE_EQUIPMENT,
    TYPE_FRAGMENT,
]


def get_item_type(item_id):
    return ConfigItemNew.get(item_id).tp


def get_equipment_level_up_needs_to_level(item_id, level):
    config = ConfigEquipmentNew.get(item_id)

    items = {}
    for i in range(0, level):
        this_level = config.levels[i]
        for _id, _amount in this_level.update_item_need:
            if _id in items:
                items[_id] += _amount
            else:
                items[_id] = _amount

    return items.items()


def make_equipment_msg(item_id, level):
    """

    :param item_id: Item id
    :param level: Item current level
    :return: Equipment Protocol Message
    :rtype: MsgEquipment
    """
    config = ConfigEquipmentNew.get(item_id)
    this_level = config.levels[level]

    msg = MsgEquipment()
    msg.level = level
    msg.attack = this_level.attack
    msg.attack_percent = this_level.attack_percent
    msg.defense = this_level.defense
    msg.defense_percent = this_level.defense_percent
    msg.manage = this_level.manage
    msg.manage_percent = this_level.manage_percent
    msg.operation = this_level.operation
    msg.operation_percent = this_level.operation_percent

    return msg


class EquipmentMaxLevel(GameException):
    pass


class Bag(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.doc = MongoBag.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoBag.document()
            self.doc['_id'] = self.char_id
            MongoBag.db(self.server_id).insert_one(self.doc)

    def check_items(self, items):
        # items [(item_id, amount)...]
        if not self.has(items):
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_ENOUGH"))

    def has(self, items):
        # items [(item_id, amount)...]

        # 把堆叠的加好， 这里算出每个物品的全部数量
        bag_items = {}
        for k, v in self.doc['slots'].iteritems():
            item_id = v['item_id']
            amount = v.get('amount', 1)
            if item_id in bag_items:
                bag_items[item_id] += amount
            else:
                bag_items[item_id] = amount

        for item_id, amount in items:
            for bag_item_id, bag_item_amount in bag_items.iteritems():
                if bag_item_id == item_id and bag_item_amount >= amount:
                    break
            else:
                return False

        return True

    def get_slot(self, slot_id):
        return self.doc['slots'][slot_id]

    def add(self, item_id, **kwargs):
        # TODO max slot amount

        config = ConfigItemNew.get(item_id)
        assert config.tp in BAG_CAN_CONTAINS_TYPE

        if config.tp == TYPE_EQUIPMENT:
            level = kwargs.get('level', 0)
            amount = kwargs.get('amount', 1)
            new_state = self._add_equipment(item_id, level, amount)
        else:
            # 这些是可以堆叠的，先找是否有格子已经是这个物品了，如果有了，再判断是否达到堆叠上限
            amount = kwargs.get('amount', 1)
            new_state = self._add_stack_item(item_id, amount)

        slot_ids = []
        updater = {}
        for slot_id, state in new_state:
            slot_ids.append(slot_id)
            self.doc['slots'][slot_id] = state
            updater['slots.{0}'.format(slot_id)] = state

        MongoBag.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_notify(slot_ids=slot_ids)

    def _add_equipment(self, item_id, level, amount):
        new_state = []
        for i in range(amount):
            slot_id = make_string_id()
            data = {
                'item_id': item_id,
                'level': level,
            }

            new_state.append((slot_id, data))

        return new_state

    def _add_stack_item(self, item_id, amount):
        stack_max = ConfigItemNew.get(item_id).stack_max
        new_state = []

        # 先尝试把物品往现有的格子中放
        remained_amount = amount
        for k, v in self.doc['slots'].iteritems():
            if not remained_amount:
                break

            if v['item_id'] != item_id:
                continue

            empty_space = stack_max - v['amount']
            if empty_space >= remained_amount:
                # 这个位置还是可以把这些amount全部装下的
                state = {
                    'item_id': item_id,
                    'amount': v['amount'] + remained_amount
                }

                remained_amount = 0
            else:
                state = {
                    'item_id': item_id,
                    'amount': stack_max
                }
                remained_amount -= empty_space

            new_state.append((k, state))

        # 把有物品的格子都跑了一遍还是有剩余的数量
        # TODO 格子总量
        while remained_amount:
            slot_id = make_string_id()
            if remained_amount <= stack_max:
                state = {
                    'item_id': item_id,
                    'amount': remained_amount
                }

                remained_amount = 0
            else:
                state = {
                    'item_id': item_id,
                    'amount': stack_max
                }

                remained_amount -= stack_max
            new_state.append((slot_id, state))

        return new_state

    def remove_by_slot_id(self, slot_id, amount):
        this_slot = self.doc['slots'][slot_id]
        bag_amount = this_slot.get('amount', 1)

        new_amount = bag_amount - amount
        if new_amount <= 0:
            self.doc['slots'].pop(slot_id)
            MongoBag.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$unset': {
                    'slots.{0}'.format(slot_id): 1
                }}
            )
            self.send_remove_notify(slots_ids=[slot_id])
        else:
            self.doc['slots'][slot_id]['amount'] = new_amount
            MongoBag.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'slots.{0}.amount'.format(slot_id): new_amount
                }}
            )

            self.send_notify(slot_ids=[slot_id])

    def remove_by_item_id(self, item_id, amount):
        assert get_item_type(item_id) != TYPE_EQUIPMENT

        slot_amount = []
        for k, v in self.doc['slots'].iteritems():
            if v['item_id'] != item_id:
                continue

            if amount == 0:
                break

            if v['amount'] >= amount:
                slot_amount.append((k, amount))
                amount = 0
            else:
                slot_amount.append((k, v['amount']))
                amount -= v['amount']

        if amount:
            # 跑了还有 amount，说明背包中的数量不足
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_ENOUGH"))

        for slot_id, amount in slot_amount:
            self.remove_by_slot_id(slot_id, amount)

    def item_use(self, slot_id):
        # 道具使用
        # TODO error handle
        """

        :rtype: ResourceClassification
        """
        this_slot = self.doc['slots'][slot_id]
        config = ConfigItemUse.get(this_slot['item_id'])

        if config.use_item_id:
            if config.use_item_id in MONEY:
                money = {
                    MONEY[config.use_item_id]: -config.use_item_amount,
                    'message': "item use: {0}".format(this_slot['item_id'])
                }
                Club(self.server_id, self.char_id).update(**money)
            else:
                self.remove_by_item_id(config.use_item_id, config.use_item_amount)

        self.remove_by_slot_id(slot_id, 1)

        result = config.using_result()

        resource_classified = ResourceClassification.classify(result)
        resource_classified.add(self.server_id, self.char_id)

        return resource_classified

    def item_merge(self, slot_id):
        # 碎片合成
        # TODO error handler
        this_slot = self.doc['slots'][slot_id]
        item_id = this_slot['item_id']
        amount = this_slot['amount']

        config = ConfigItemMerge.get(item_id)
        if amount < config.amount:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_ENOUGH"))

        self.remove_by_slot_id(slot_id, config.amount)

        resource_classified = ResourceClassification.classify([(config.to_id, 1)])
        resource_classified.add(self.server_id, self.char_id)
        return resource_classified

    def item_destroy(self, slot_id):
        # 碎片销毁
        item_id = self.doc['slots'][slot_id]['item_id']
        amount = self.doc['slots'][slot_id]['amount']

        tp = get_item_type(item_id)
        assert tp == TYPE_FRAGMENT
        self.remove_by_slot_id(slot_id, amount)

        config = ConfigItemMerge.get(item_id)
        drop = []
        if config.renown:
            drop.append((money_text_to_item_id('renown'), config.renown))
        if config.crystal:
            drop.append((money_text_to_item_id('crystal'), config.crystal))

        resource_classified = ResourceClassification.classify(drop)
        resource_classified.add(self.server_id, self.char_id)
        return resource_classified


    def equipment_destroy(self, slot_id, use_sycee):
        # 装备销毁
        """

        :rtype: ResourceClassification
        """
        from core.staff import StaffManger

        this_slot = self.doc['slots'][slot_id]
        item_id = this_slot['item_id']

        if get_item_type(item_id) != TYPE_EQUIPMENT:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if StaffManger(self.server_id, self.char_id).is_equip_on_staff(slot_id):
            raise GameException(ConfigErrorMessage.get_error_id("EQUIPMENT_CANNOT_DESTROY_ON_STAFF"))

        level = this_slot['level']
        results = get_equipment_level_up_needs_to_level(item_id, level)

        if use_sycee:
            diamond = GlobalConfig.value("EQUIPMENT_DESTROY_SYCEE")
            Club(self.server_id, self.char_id).update(diamond=-diamond,
                                                      message='Equipment Destroy: {0}'.format(item_id))

            MongoBag.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'slots.{0}.level'.format(slot_id): 0
                }}
            )
            self.doc['slots'][slot_id]['level'] = 0
            self.send_notify(slot_ids=[slot_id])
        else:
            self.remove_by_slot_id(slot_id, 1)

        resource_classified = ResourceClassification.classify(results)
        resource_classified.add(self.server_id, self.char_id)
        return resource_classified


    def equipment_level_up_preview(self, slot_id):
        # 装备升级准备
        # 客户端请求一下，把计算好的下一级属性发回去， 先不升级
        this_slot = self.doc['slots'][slot_id]
        item_id = this_slot['item_id']
        level = this_slot['level']

        config = ConfigEquipmentNew.get(item_id)
        # TODO check exists

        max_level = min(config.max_level, get_club_property(self.server_id, self.char_id, 'level') * 2)
        if level >= max_level:
            raise GameException(ConfigErrorMessage.get_error_id("EQUIPMENT_REACH_MAX_LEVEL"))

        return make_equipment_msg(item_id, level + 1)

    def equipment_level_up_confirm(self, slot_id, times=1):
        # 装备升级确认
        # 上一步 用户看到下一级属性后， 点击确认升级
        this_slot = self.doc['slots'][slot_id]
        item_id = this_slot['item_id']
        level = this_slot['level']

        config = ConfigEquipmentNew.get(item_id)
        max_level = min(config.max_level, get_club_property(self.server_id, self.char_id, 'level') * 2)

        def do_level_up(_level):
            if _level >= max_level:
                raise GameException(ConfigErrorMessage.get_error_id("EQUIPMENT_REACH_MAX_LEVEL"))

            item_needs = config.levels[_level].update_item_need

            resource_classified = ResourceClassification.classify(item_needs)
            resource_classified.check_exist(self.server_id, self.char_id)
            resource_classified.remove(self.server_id, self.char_id)

            return _level + 1

        error_code = 0
        old_level = level
        for i in range(times):
            try:
                level = do_level_up(level)
            except GameException as e:
                error_code = e.error_id
                break

        levelup = False
        if level > old_level:
            levelup = True
            self.doc['slots'][slot_id]['level'] = level

            MongoBag.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'slots.{0}.level'.format(slot_id): level
                }}
            )

        self.send_notify(slot_ids=[slot_id])
        return error_code, levelup, make_equipment_msg(item_id, level)

    def send_remove_notify(self, slots_ids):
        notify = BagSlotsRemoveNotify()
        notify.slot_id.extend(slots_ids)
        MessagePipe(self.char_id).put(msg=notify)

    def send_notify(self, slot_ids=None):
        if slot_ids:
            act = ACT_UPDATE
        else:
            slot_ids = self.doc['slots'].keys()
            act = ACT_INIT

        notify = BagSlotsNotify()
        notify.act = act
        notify.equipment_max_amount = BAG_EQUIPMENT_MAX_AMOUNT
        notify.fragment_max_amount = BAG_FRAGMENT_MAX_AMOUNT
        notify.other_max_amount = BAG_STUFF_MAX_AMOUNT

        for i in slot_ids:
            this_slot = self.doc['slots'][i]

            notify_slot = notify.slots.add()
            notify_slot.id = i
            notify_slot.item_id = this_slot['item_id']
            notify_slot.amount = this_slot.get('amount', 1)

            if get_item_type(this_slot['item_id']) == 4:
                # 装备
                notify_slot.equipment.MergeFrom(make_equipment_msg(this_slot['item_id'], this_slot['level']))

        MessagePipe(self.char_id).put(msg=notify)
