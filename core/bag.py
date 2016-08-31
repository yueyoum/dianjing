# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       bag
Date Created:   2016-03-10 10-37
Description:

"""
import math
from collections import OrderedDict

from dianjing.exception import GameException

from core.mongo import MongoBag
from core.club import Club, get_club_property
from core.resource import ResourceClassification, money_text_to_item_id
from core.value_log import ValueLogEquipmentLevelUpTimes

from utils.functional import make_string_id
from utils.message import MessagePipe

from config import (
    ConfigErrorMessage,
    ConfigItemNew,
    ConfigEquipmentNew,
    ConfigItemUse,
    ConfigItemMerge,
    GlobalConfig,

    ConfigEquipmentSpecial,
    ConfigEquipmentSpecialGrowingProperty,
    ConfigEquipmentSpecialLevel,
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
from protomsg.common_pb2 import (
    PROPERTY_STAFF_ATTACK,
    PROPERTY_STAFF_ATTACK_PERCENT,
    PROPERTY_STAFF_DEFENSE,
    PROPERTY_STAFF_DEFENSE_PERCENT,
    PROPERTY_STAFF_MANAGE,
    PROPERTY_STAFF_MANAGE_PERCENT,
    PROPERTY_STAFF_OPERATION,
    PROPERTY_STAFF_OPERATION_PERCENT,

    PROPERTY_UNIT_HP_PERCENT,
    PROPERTY_UNIT_ATTACK_PERCENT,
    PROPERTY_UNIT_DEFENSE_PERCENT,
    PROPERTY_UNIT_HIT_PERCENT,
    PROPERTY_UNIT_DODGE_PERCENT,
    PROPERTY_UNIT_CRIT_PERCENT,
    PROPERTY_UNIT_TOUGHNESS_PERCENT,
    PROPERTY_UNIT_CRIT_MULTIPLE,

    PROPERTY_UNIT_HURT_ADDIITON_TO_TERRAN,
    PROPERTY_UNIT_HURT_ADDIITON_TO_PROTOSS,
    PROPERTY_UNIT_HURT_ADDIITON_TO_ZERG,
    PROPERTY_UNIT_HURT_ADDIITON_BY_TERRAN,
    PROPERTY_UNIT_HURT_ADDIITON_BY_PROTOSS,
    PROPERTY_UNIT_HURT_ADDIITON_BY_ZERG,

    PROPERTY_UNIT_FINAL_HURT_ADDITION,
    PROPERTY_UNIT_FINAL_HURT_REDUCE,
)

PROPERTY_TO_NAME_MAP = {
    PROPERTY_STAFF_ATTACK: 'staff_attack',
    PROPERTY_STAFF_ATTACK_PERCENT: 'staff_attack_percent',
    PROPERTY_STAFF_DEFENSE: 'staff_defense',
    PROPERTY_STAFF_DEFENSE_PERCENT: 'staff_defense_percent',
    PROPERTY_STAFF_MANAGE: 'staff_manage',
    PROPERTY_STAFF_MANAGE_PERCENT: 'staff_manage_percent',
    PROPERTY_STAFF_OPERATION: 'staff_operation',
    PROPERTY_STAFF_OPERATION_PERCENT: 'staff_operation_percent',

    PROPERTY_UNIT_HP_PERCENT: 'unit_hp_percent',
    PROPERTY_UNIT_ATTACK_PERCENT: 'unit_attack_percent',
    PROPERTY_UNIT_DEFENSE_PERCENT: 'unit_defense_percent',
    PROPERTY_UNIT_HIT_PERCENT: 'unit_hit_percent',
    PROPERTY_UNIT_DODGE_PERCENT: 'unit_dodge_percent',
    PROPERTY_UNIT_CRIT_PERCENT: 'unit_crit_percent',
    PROPERTY_UNIT_TOUGHNESS_PERCENT: 'unit_toughness_percent',
    PROPERTY_UNIT_CRIT_MULTIPLE: 'unit_crit_multiple',

    PROPERTY_UNIT_HURT_ADDIITON_TO_TERRAN: 'unit_hurt_addition_to_terran',
    PROPERTY_UNIT_HURT_ADDIITON_TO_PROTOSS: 'unit_hurt_addition_to_protoss',
    PROPERTY_UNIT_HURT_ADDIITON_TO_ZERG: 'unit_hurt_addition_to_zerg',
    PROPERTY_UNIT_HURT_ADDIITON_BY_TERRAN: 'unit_hurt_addition_by_terran',
    PROPERTY_UNIT_HURT_ADDIITON_BY_PROTOSS: 'unit_hurt_addition_by_protoss',
    PROPERTY_UNIT_HURT_ADDIITON_BY_ZERG: 'unit_hurt_addition_by_zerg',
    PROPERTY_UNIT_FINAL_HURT_ADDITION: 'unit_final_hurt_addition',
    PROPERTY_UNIT_FINAL_HURT_REDUCE: 'unit_final_hurt_reduce'
}

NAME_TO_PROPERTY_MAP = {v: k for k, v in PROPERTY_TO_NAME_MAP.iteritems()}

TYPE_ITEM_NORMAL = 1  # 普通道具
TYPE_ITEM_CAN_USE = 2  # 可使用道具
TYPE_MONEY = 3  # 代币 -- 不会进包裹
TYPE_EQUIPMENT = 4  # 装备
TYPE_FRAGMENT = 5  # 碎片
TYPE_STAFF = 6  # 选手 -- 不会进包裹

TYPE_EQUIPMENT_SUB_TYPE_SPECIAL = 1

BAG_CAN_CONTAINS_TYPE = [
    TYPE_ITEM_NORMAL,
    TYPE_ITEM_CAN_USE,
    TYPE_EQUIPMENT,
    TYPE_FRAGMENT,
]

SPECIAL_EQUIPMENT_BASE_PROPERTY = [
    PROPERTY_STAFF_ATTACK, PROPERTY_STAFF_DEFENSE, PROPERTY_STAFF_MANAGE
]


def get_item_type(item_id):
    return ConfigItemNew.get(item_id).tp


def get_equipment_level_up_needs_to_level(item_id, level, prob=100):
    config = ConfigEquipmentNew.get(item_id)

    items = {}
    for i in range(0, level):
        this_level = config.levels[i]
        for _id, _amount in this_level.update_item_need:
            if _id in items:
                items[_id] += _amount
            else:
                items[_id] = _amount

    results = []
    for k, v in items.iteritems():
        v = v * prob / 100
        if v:
            results.append((k, v))

    return results


class Equipment(object):
    __slots__ = [
        'id', 'level',

        'growing', 'properties', 'skills', 'is_special',

        'staff_attack', 'staff_attack_percent',
        'staff_defense', 'staff_defense_percent',
        'staff_manage', 'staff_manage_percent',
        'staff_operation', 'staff_operation_percent',

        'unit_hp_percent', 'unit_attack_percent',
        'unit_defense_percent', 'unit_hit_percent',
        'unit_dodge_percent', 'unit_crit_percent',
        'unit_toughness_percent', 'unit_crit_multiple',

        'unit_hurt_addition_to_terran',
        'unit_hurt_addition_to_protoss',
        'unit_hurt_addition_to_zerg',
        'unit_hurt_addition_by_terran',
        'unit_hurt_addition_by_protoss',
        'unit_hurt_addition_by_zerg',

        'unit_final_hurt_addition',
        'unit_final_hurt_reduce',
    ]

    def __init__(self):
        self.id = 0
        self.level = 0
        self.growing = 0
        self.properties = {}  # tp: level
        self.skills = {}
        self.is_special = False

        self.staff_attack = 0
        self.staff_attack_percent = 0
        self.staff_defense = 0
        self.staff_defense_percent = 0
        self.staff_manage = 0
        self.staff_manage_percent = 0
        self.staff_operation = 0
        self.staff_operation_percent = 0

        self.unit_hp_percent = 0
        self.unit_attack_percent = 0
        self.unit_defense_percent = 0
        self.unit_hit_percent = 0
        self.unit_dodge_percent = 0
        self.unit_crit_percent = 0
        self.unit_toughness_percent = 0
        self.unit_crit_multiple = 0

        self.unit_hurt_addition_to_terran = 0
        self.unit_hurt_addition_to_protoss = 0
        self.unit_hurt_addition_to_zerg = 0
        self.unit_hurt_addition_by_terran = 0
        self.unit_hurt_addition_by_protoss = 0
        self.unit_hurt_addition_by_zerg = 0

        self.unit_final_hurt_addition = 0
        self.unit_final_hurt_reduce = 0

    @classmethod
    def load_from_slot_data(cls, data):
        obj = cls()
        obj.id = data['item_id']
        obj.level = data['level']

        if ConfigItemNew.get(obj.id).sub_tp == TYPE_EQUIPMENT_SUB_TYPE_SPECIAL:
            obj.is_special = True
            obj.growing = data['growing']

            config = ConfigEquipmentSpecialGrowingProperty.get_by_growing(data['growing'])
            obj.properties = OrderedDict(zip(data['properties'], config.property_active_levels))
            obj.skills = OrderedDict(zip(data['skills'], config.skill_active_levels))

        obj.calculate()
        return obj

    @classmethod
    def initialize_for_special(cls, _id, growing, properties, skills):
        config = ConfigEquipmentSpecialGrowingProperty.get_by_growing(growing)

        obj = cls()
        obj.id = _id
        obj.level = 0
        obj.is_special = True
        obj.properties = OrderedDict(zip(properties, config.property_active_levels))
        obj.skills = OrderedDict(zip(skills), config.skill_active_levels)

        obj.calculate()
        return obj

    @classmethod
    def initialize_for_normal(cls, _id):
        obj = cls()
        obj.id = _id
        obj.level = 0
        obj.calculate()
        return obj

    def calculate(self):
        if self.is_special:
            config = ConfigEquipmentSpecial.get(self.id)
            for k in NAME_TO_PROPERTY_MAP:
                v = getattr(config, k, 0)
                if v:
                    setattr(self, k, v)

            self.staff_attack = config.staff_attack + config.staff_attack * self.level * math.pow(self.growing, 1.25)
            self.staff_defense = config.staff_defense + config.staff_defense * self.level * math.pow(self.growing, 1.25)
            self.staff_manage = config.staff_manage + config.staff_manage * self.level * math.pow(self.growing, 1.25)

            self.staff_attack = int(round(self.staff_attack))
            self.staff_defense = int(round(self.staff_defense))
            self.staff_manage = int(round(self.staff_manage))

        else:
            config = ConfigEquipmentNew.get(self.id).levels[self.level]
            self.staff_attack = config.attack
            self.staff_attack_percent = config.attack_percent
            self.staff_defense = config.defense
            self.staff_defense_percent = config.defense_percent
            self.staff_manage = config.manage
            self.staff_manage_percent = config.manage_percent
            self.staff_operation = config.operation
            self.staff_operation_percent = config.operation_percent

    def get_property_value(self, p):
        name = PROPERTY_TO_NAME_MAP[p]
        return getattr(self, name)

    def make_protomsg(self):
        msg = MsgEquipment()

        msg.id = self.id
        msg.level = self.level

        if self.is_special:
            msg.growing = self.growing
            properties = [(i, 0) for i in SPECIAL_EQUIPMENT_BASE_PROPERTY] + self.properties.items()
        else:
            properties = [
                (PROPERTY_STAFF_ATTACK, 0), (PROPERTY_STAFF_ATTACK_PERCENT, 0),
                (PROPERTY_STAFF_DEFENSE, 0), (PROPERTY_STAFF_DEFENSE_PERCENT, 0),
                (PROPERTY_STAFF_MANAGE, 0), (PROPERTY_STAFF_MANAGE_PERCENT, 0),
                (PROPERTY_STAFF_OPERATION, 0), (PROPERTY_STAFF_OPERATION_PERCENT, 0),
            ]

        for p, lv in properties:
            msg_property = msg.properties.add()
            msg_property.tp = p
            msg_property.level = lv
            msg_property.value = self.get_property_value(p)

        for s, lv in self.skills:
            msg_skill = msg.skills.add()
            msg_skill.id = s
            msg_skill.level = lv

        return msg

    def to_doc(self):
        doc = {
            'item_id': self.id,
            'amount': 1,
            'level': self.level
        }

        if self.is_special:
            doc.update({
                'growing': self.growing,
                'properties': self.properties.keys(),
                'skills': self.skills.keys(),
            })

        return doc

    def get_level_up_needs_items(self, add_level):
        item_needs = []
        this_level = self.level

        if self.is_special:
            for _ in range(add_level):
                item = ConfigEquipmentSpecialLevel.get(this_level).items
                item = [(k, int(v * self.growing)) for k, v in item]
                item_needs.extend(item)

                this_level += 1
        else:
            config = ConfigEquipmentNew.get(self.id)
            for _ in range(add_level):
                item = config.levels[this_level].update_item_need
                item_needs.extend(item)
                this_level += 1

        return item_needs


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
            if not ConfigEquipmentNew.get(item_id).levels:
                raise GameException(ConfigErrorMessage.get_error_id("EQUIPMENT_HAS_NO_LEVEL_CAN_NOT_ADD"))

            level = kwargs.get('level', 0)
            amount = kwargs.get('amount', 1)
            new_state = self.add_equipment(item_id, level, amount)
        else:
            # 这些是可以堆叠的，先找是否有格子已经是这个物品了，如果有了，再判断是否达到堆叠上限
            amount = kwargs.get('amount', 1)
            new_state = self.add_stack_item(item_id, amount)

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

    def add_equipment(self, item_id, level, amount):
        new_state = []
        for i in range(amount):
            slot_id = make_string_id()
            data = {
                'item_id': item_id,
                'level': level,
            }

            new_state.append((slot_id, data))

        return new_state

    def add_equipment_object(self, equip):
        """

        :type equip: Equipment
        """
        slot_id = make_string_id()
        data = equip.to_doc()

        self.doc['slots'][slot_id] = data
        MongoBag.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'slots.{0}'.format(slot_id): data
            }}
        )

        self.send_notify(slot_ids=[slot_id])

    def add_stack_item(self, item_id, amount):
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

    def item_use(self, slot_id, amount):
        # 道具使用
        """

        :rtype: ResourceClassification
        """
        this_slot = self.doc['slots'][slot_id]
        item_amount = this_slot.get('amount', 1)
        if amount > item_amount:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_ENOUGH"))

        config = ConfigItemUse.get(this_slot['item_id'])

        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_CANNOT_USE"))

        if config.use_item_id:
            cost = [(config.use_item_id, config.use_item_amount * amount)]
            rc = ResourceClassification.classify(cost)
            rc.check_exist(self.server_id, self.char_id)
            rc.remove(self.server_id, self.char_id)

        result = {}
        for i in range(amount):
            for _id, _amount in config.using_result():
                if _id in result:
                    result[_id] += _amount
                else:
                    result[_id] = _amount

        self.remove_by_slot_id(slot_id, amount)

        resource_classified = ResourceClassification.classify(result.items())
        resource_classified.add(self.server_id, self.char_id)
        return resource_classified

    def item_merge(self, slot_id):
        # 碎片合成
        try:
            this_slot = self.doc['slots'][slot_id]
        except KeyError:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

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
            drop.append((money_text_to_item_id('renown'), config.renown * amount))
        if config.crystal:
            drop.append((money_text_to_item_id('crystal'), config.crystal * amount))

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

        if StaffManger(self.server_id, self.char_id).find_staff_id_with_equip(slot_id):
            raise GameException(ConfigErrorMessage.get_error_id("EQUIPMENT_CANNOT_DESTROY_ON_STAFF"))

        config = ConfigEquipmentNew.get(item_id)
        level = this_slot['level']

        if use_sycee:
            min_level = min(config.levels.keys())
            if level == min_level:
                raise GameException(ConfigErrorMessage.get_error_id("EQUIPMENT_CANNOT_DESTROY_NO_LEVEL_UP"))

            diamond = GlobalConfig.value("EQUIPMENT_DESTROY_SYCEE")
            rf = ResourceClassification.classify([(money_text_to_item_id('diamond'), diamond)])
            rf.check_exist(self.server_id, self.char_id)
            rf.remove(self.server_id, self.char_id)

            MongoBag.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'slots.{0}.level'.format(slot_id): 0
                }}
            )
            self.doc['slots'][slot_id]['level'] = 0
            self.send_notify(slot_ids=[slot_id])

            results = get_equipment_level_up_needs_to_level(item_id, level, prob=100)
        else:
            self.remove_by_slot_id(slot_id, 1)
            results = get_equipment_level_up_needs_to_level(item_id, level, prob=70)
            results.append((money_text_to_item_id('renown'), config.renown))

        resource_classified = ResourceClassification.classify(results)
        resource_classified.add(self.server_id, self.char_id)
        return resource_classified

    def equipment_level_up(self, slot_id, times=1):
        from core.staff import StaffManger
        from core.formation import Formation
        from core.plunder import Plunder

        this_slot = self.doc['slots'][slot_id]
        item_id = this_slot['item_id']

        if get_item_type(item_id) != TYPE_EQUIPMENT:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        equip = Equipment.load_from_slot_data(this_slot)
        level = equip.level

        if equip.is_special:
            max_level = Plunder(self.server_id, self.char_id).get_station_level()
        else:
            config = ConfigEquipmentNew.get(item_id)
            max_level = min(config.max_level, get_club_property(self.server_id, self.char_id, 'level') * 2)

        if level >= max_level:
            raise GameException(ConfigErrorMessage.get_error_id("EQUIPMENT_REACH_MAX_LEVEL"))

        can_add_level = max_level - level
        if times > can_add_level:
            times = can_add_level

        def do_level_up(_add):
            _item_needs = equip.get_level_up_needs_items(_add)

            resource_classified = ResourceClassification.classify(_item_needs)
            resource_classified.check_exist(self.server_id, self.char_id)
            resource_classified.remove(self.server_id, self.char_id)

        old_level = level
        error_code = 0

        for i in range(times, 0, -1):
            try:
                do_level_up(i)
            except GameException as e:
                error_code = e.error_id
            else:
                level += i
                break

        if level > old_level:
            self.doc['slots'][slot_id]['level'] = level

            MongoBag.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'slots.{0}.level'.format(slot_id): level
                }}
            )

            ValueLogEquipmentLevelUpTimes(self.server_id, self.char_id).record(value=level - old_level)
            self.send_notify(slot_ids=[slot_id])

            sm = StaffManger(self.server_id, self.char_id)
            staff_id = sm.find_staff_id_with_equip(slot_id)
            if staff_id:
                fm = Formation(self.server_id, self.char_id)
                if staff_id in fm.in_formation_staffs():
                    s_obj = sm.get_staff_object(staff_id)
                    s_obj.calculate()
                    s_obj.make_cache()

                    Club(self.server_id, self.char_id).send_notify()

        return error_code, level != old_level, Equipment.load_from_slot_data(self.doc['slots'][slot_id])

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
                equip = Equipment.load_from_slot_data(this_slot)
                notify_slot.equipment.MergeFrom(equip.make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)
