# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       bag
Date Created:   2016-03-10 10-37
Description:

"""
from dianjing.exception import GameException

from core.mongo import MongoBag

from utils.functional import make_string_id
from utils.message import MessagePipe

from config import ConfigErrorMessage, ConfigItemNew, ConfigEquipmentNew, ConfigItemUse, ConfigItemMerge
from config.settings import BAG_EQUIPMENT_MAX_AMOUNT, BAG_FRAGMENT_MAX_AMOUNT, BAG_STUFF_MAX_AMOUNT

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.bag_pb2 import (
    BagSlotsNotify,
    BagSlotsRemoveNotify
)

DAIBI = [30000, 30001, 30002, 30003, 30004]


def get_item_type(item_id):
    return ConfigItemNew.get(item_id).tp


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
            new_state = self._add_equipment(item_id, level)
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
        # TODO equipment
        new_amount = this_slot['amount'] - amount
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

    def use(self, slot_id):
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

    def merge(self, slot_id):
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

    def destroy(self, slot_id):
        item_id = self.doc['slots'][slot_id]['item_id']
        tp = get_item_type(item_id)
        assert tp in [4, 5]

        # TODO destroy reward
        self.remove_by_slot_id(slot_id, 1)

    def equipment_level_up(self, slot_id):
        this_slot = self.doc['slots'][slot_id]
        item_id = this_slot['item_id']
        level = this_slot['level']
        item_needs = ConfigEquipmentNew.get(item_id).levels[level].update_item_need

        if not item_needs:
            # TODO max level
            raise Exception("max level")

        bag_items = []
        for item_id, amount in item_needs:
            if item_id in DAIBI:
                # TODO
                continue

            bag_items.append((item_id, amount))

        if not self.has(bag_items):
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_ENOUGH"))

        for item_id, amount in bag_items:
            self.remove_by_item_id(item_id, amount)

        self.doc['slots'][slot_id]['level'] += 1
        MongoBag.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {
                'slots.{0}.level'.format(slot_id): 1
            }}
        )

        self.send_notify(slot_ids=[slot_id])

    def _add_equipment(self, item_id, level):
        slot_id = make_string_id()
        data = {
            'item_id': item_id,
            'level': level,
        }

        return [(slot_id, data)]

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
                config_equipment = ConfigEquipmentNew.get(this_slot['item_id'])
                this_level = config_equipment.levels[this_slot['level']]
                notify_slot.equipment.level = this_slot['level']
                notify_slot.equipment.attack = this_level.attack
                notify_slot.equipment.attack_percent = this_level.attack
                notify_slot.equipment.defense = this_level.defense
                notify_slot.equipment.defense_percent = this_level.defense_percent
                notify_slot.equipment.manage = this_level.manage
                notify_slot.equipment.manage_percent = this_level.manage_percent
                notify_slot.equipment.operation = this_level.cost
                notify_slot.equipment.operation_percent = this_level.cost_percent

        MessagePipe(self.char_id).put(msg=notify)
