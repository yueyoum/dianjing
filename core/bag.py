# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       bag
Date Created:   2016-03-10 10-37
Description:

"""
from dianjing.exception import GameException

from core.mongo import MongoBag
from core.resource import Resource

from utils.functional import make_string_id
from utils.message import MessagePipe

from config import ConfigErrorMessage, ConfigItemNew, ConfigEquipmentNew, ConfigItemUse, ConfigItemMerge, GlobalConfig
from config.settings import BAG_EQUIPMENT_MAX_AMOUNT, BAG_FRAGMENT_MAX_AMOUNT, BAG_STUFF_MAX_AMOUNT

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.bag_pb2 import (
    BagSlotsNotify,
    BagSlotsRemoveNotify,
    Equipment as MsgEquipment,
)

DAIBI = [30000, 30001, 30002, 30003, 30004]


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
    msg.operation = this_level.cost
    msg.operation_percent = this_level.cost_percent

    return msg


class EquipmentLevelUpError(Exception):
    pass

class EquipmentMaxLevel(EquipmentLevelUpError):
    pass

class NoItems(EquipmentLevelUpError):
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

    def has(self, data):
        # data [(item_id, amount), ...]
        bag_items = {}
        for k, v in self.doc['slots'].iteritems():
            item_id = v['item_id']
            amount = v.get('amount', 1)
            if item_id in bag_items:
                bag_items[item_id] += amount
            else:
                bag_items[item_id] = amount

        for item_id, amount in data:
            for bag_item_id, bag_item_amount in bag_items.iteritems():
                if bag_item_id == item_id and bag_item_amount >= amount:
                    break
            else:
                return False

        return True

    def add(self, item_id, **kwargs):
        # TODO max slot amount

        config = ConfigItemNew.get(item_id)
        assert config.tp in [1, 2, 4, 5]

        if config.tp == 4:
            # 装备
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
        # TODO equipment

        slot_amount = []
        for k, v in self.doc['slots'].iteritems():
            if v['item_id'] != item_id:
                continue

            if v['amount'] >= amount:
                slot_amount.append((k, amount))
            else:
                slot_amount.append((k, v['amount']))
                amount -= v['amount']

        for slot_id, amount in slot_amount:
            self.remove_by_slot_id(slot_id, amount)

    def item_use(self, slot_id):
        # TODO error handle
        this_slot = self.doc['slots'][slot_id]
        config = ConfigItemUse.get(this_slot['item_id'])

        if config.use_item_id:
            if config.use_item_id in DAIBI:
                # TODO 代币
                pass
            else:
                if not self.has([(config.use_item_id, config.use_item_amount)]):
                    raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_ENOUGH"))

                self.remove_by_item_id(config.use_item_id, config.use_item_amount)

        self.remove_by_slot_id(slot_id, 1)

        result = config.using_result()
        for item_id, amount in result:
            if item_id in DAIBI:
                # TODO
                pass
            else:
                if get_item_type(item_id) == 4:
                    # 装备
                    for i in range(amount):
                        self.add(item_id)
                else:
                    self.add(item_id, amount=amount)

        return result

    def item_merge(self, slot_id):
        # TODO error handler
        this_slot = self.doc['slots'][slot_id]
        item_id = this_slot['item_id']
        amount = this_slot['amount']

        config = ConfigItemMerge.get(item_id)
        if amount < config.amount:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_ENOUGH"))

        self.remove_by_slot_id(slot_id, config.amount)

        if config.to_id in DAIBI:
            # TODO
            pass
        else:
            self.add(config.to_id, amount=1)

    def item_destroy(self, slot_id):
        item_id = self.doc['slots'][slot_id]['item_id']
        tp = get_item_type(item_id)
        assert tp in [4, 5]

        # TODO destroy reward
        self.remove_by_slot_id(slot_id, 1)

    def equipment_destroy(self, slot_id, use_sycee):
        this_slot = self.doc['slots'][slot_id]
        item_id = this_slot['item_id']

        if get_item_type(item_id) != 4:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        level = this_slot['level']
        items = get_equipment_level_up_needs_to_level(item_id, level)

        if use_sycee:
            sycee = GlobalConfig.value("EQUIPMENT_DESTROY_SYCEE")
            with Resource(self.server_id, self.char_id).check(sycee=-sycee, message="Equipment Destroy"):
                pass

            MongoBag.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'slots.{0}.level'.format(slot_id): 0
                }}
            )
        else:
            self.remove_by_slot_id(slot_id, 1)

        # TODO daibi
        for a, b in items:
            if a not in DAIBI:
                self.add(a, amount=b)

        return items

    def equipment_level_up(self, slot_id):
        this_slot = self.doc['slots'][slot_id]
        item_id = this_slot['item_id']
        level = this_slot['level']
        item_needs = ConfigEquipmentNew.get(item_id).levels[level].update_item_need

        if not item_needs:
            # TODO max level
            raise Exception("max level")

        bag_items = []
        for a, b in item_needs:
            if a in DAIBI:
                # TODO
                continue

            bag_items.append((a, b))

        if not self.has(bag_items):
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_ENOUGH"))

        return make_equipment_msg(item_id, level+1)


    def equipment_level_up_confirm(self, slot_id, times=1):
        this_slot = self.doc['slots'][slot_id]
        item_id = this_slot['item_id']
        level = this_slot['level']

        config = ConfigEquipmentNew.get(item_id)

        def do_level_up(_item_id, _level):
            item_needs = config.levels[level].update_item_need

            if not item_needs:
                # TODO max level
                raise EquipmentMaxLevel()

            bag_items = []
            for a, b in item_needs:
                if a in DAIBI:
                    # TODO
                    continue

                bag_items.append((a, b))

            if not self.has(bag_items):
                raise NoItems()

            for a, b in bag_items:
                self.remove_by_item_id(a, b)

            return _level + 1

        old_level = level
        equipment_messages = []
        for i in range(times):
            try:
                level = do_level_up(item_id, level)
            except EquipmentLevelUpError:
                break

            equipment_messages.append((make_equipment_msg(item_id, level)))

        if level > old_level:
            self.doc['slots'][slot_id]['level'] = level

            MongoBag.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'slots.{0}.level'.format(slot_id): level
                }}
            )

        self.send_notify(slot_ids=[slot_id])
        return equipment_messages


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

        while remained_amount:
            # 把有物品的格子都跑了一遍还是有剩余的数量
            # TODO 格子总量
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
