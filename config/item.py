# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       item
Date Created:   2015-10-21 15:33
Description:

"""

import copy
import random
from config.base import ConfigBase


class ItemNew(object):
    __slots__ = [
        'id', 'name', 'tp', 'sub_tp', 'quality', 'stack_max'
    ]

    def __init__(self):
        self.id = 0
        self.name = ""
        self.tp = 0
        self.sub_tp = 0
        self.quality = 0
        self.stack_max = 0

class ItemUse(object):
    __slots__ = [
        'id', 'use_item_id', 'use_item_amount', 'result'
    ]

    def __init__(self):
        self.id = 0
        self.use_item_id = 0
        self.use_item_amount = 0
        self.result = []

    def using_result(self):
        result = {}
        for group in self.result:
            item = copy.deepcopy(group)
            for i in range(1, len(item)):
                item[i][2] += item[i-1][2]

            prob = random.randint(1, 1000)
            for _id, _amount, _prob in item:
                if _prob >= prob:
                    if _id in result:
                        result[_id] += _amount
                    else:
                        result[_id] = _amount

                    break

        return result.items()


class ItemMerge(object):
    __slots__ = [
        'id', 'amount', 'to_id', 'renown', 'crystal'
    ]

    def __init__(self):
        self.id = 0
        self.amount = 0
        self.to_id = 0
        self.renown = 0
        self.crystal = 0


class EquipmentLevel(object):
    __slots__ = [
        'attack', 'attack_percent', 'defense', 'defense_percent',
        'manage', 'manage_percent', 'operation', 'operation_percent',
        'update_item_need'
    ]

    @classmethod
    def create(cls, data):
        obj = cls()
        for key in cls.__slots__:
            setattr(obj, key, data[key])

        return obj

    def __init__(self):
        self.attack = 0
        self.attack_percent = 0
        self.defense = 0
        self.defense_percent = 0
        self.manage = 0
        self.manage_percent = 0
        self.operation = 0
        self.operation_percent = 0
        self.update_item_need = []


class EquipmentNew(object):
    __slots__ = [
        'id', 'tp', 'renown', 'max_level', 'levels'
    ]

    def __init__(self):
        self.id = 0
        self.tp = 0
        self.renown = 0
        self.max_level = 0
        self.levels = {}
        """:type: dict[int, EquipmentLevel]"""


class ConfigItemNew(ConfigBase):
    EntityClass = ItemNew
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: ItemNew
        """
        return super(ConfigItemNew, cls).get(_id)

class ConfigItemUse(ConfigBase):
    EntityClass = ItemUse
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: ItemUse
        """
        return super(ConfigItemUse, cls).get(_id)


class ConfigItemMerge(ConfigBase):
    EntityClass = ItemMerge
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: ItemMerge
        """
        return super(ConfigItemMerge, cls).get(_id)


class ConfigEquipmentNew(ConfigBase):
    EntityClass = EquipmentNew
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigEquipmentNew, cls).initialize(fixture)
        for obj in cls.INSTANCES.values():
            levels = {}
            for k, v in obj.levels.iteritems():
                levels[int(k)] = EquipmentLevel.create(v)

            obj.levels = levels

    @classmethod
    def get(cls, _id):
        """

        :rtype: EquipmentNew
        """
        return super(ConfigEquipmentNew, cls).get(_id)



class EquipmentSpecial(object):
    __slots__ = [
        'id',
        'staff_attack', 'staff_defense', 'staff_manage',
        'staff_attack_percent', 'staff_defense_percent', 'staff_manage_percent',
        'unit_attack_percent', 'unit_defense_percent', 'unit_hp_percent',
        'unit_hit_rate', 'unit_dodge_rate', 'unit_crit_rate',
        'unit_toughness_rate', 'unit_crit_multiple',

        'unit_hurt_addition_to_terran',
        'unit_hurt_addition_to_protoss',
        'unit_hurt_addition_to_zerg',
        'unit_hurt_addition_by_terran',
        'unit_hurt_addition_by_protoss',
        'unit_hurt_addition_by_zerg',

        'skills',
    ]

    def __init__(self):
        self.id = 0
        self.staff_attack = 0
        self.staff_defense = 0
        self.staff_manage = 0

        self.staff_attack_percent = 0
        self.staff_defense_percent = 0
        self.staff_manage_percent = 0

        self.unit_attack_percent = 0
        self.unit_defense_percent = 0
        self.unit_hp_percent = 0
        self.unit_hit_rate = 0
        self.unit_dodge_rate = 0
        self.unit_crit_rate = 0
        self.unit_toughness_rate = 0
        self.unit_crit_multiple = 0
        self.unit_hurt_addition_to_terran = 0
        self.unit_hurt_addition_to_protoss = 0
        self.unit_hurt_addition_to_zerg = 0
        self.unit_hurt_addition_by_terran = 0
        self.unit_hurt_addition_by_protoss = 0
        self.unit_hurt_addition_by_zerg = 0
        self.skills = []



class ConfigEquipmentSpecial(ConfigBase):
    EntityClass = EquipmentSpecial
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: EquipmentSpecial
        """
        return super(ConfigEquipmentSpecial, cls).get(_id)


class EquipmentSpecialGrowingProperty(object):
    __slots__ = [
        'id', 'growing_low', 'growing_high',
        'property_active_levels',
        'skill_active_levels'
    ]

    def __init__(self):
        self.id = 0
        self.growing_low = 0
        self.growing_high = 0
        self.property_active_levels = []
        self.skill_active_levels = []


class ConfigEquipmentSpecialGrowingProperty(ConfigBase):
    EntityClass = EquipmentSpecialGrowingProperty
    INSTANCES = {}
    FILTER_CACHE = {}

    MAP = {}

    @classmethod
    def get_by_growing(cls, value):
        """

        :rtype: EquipmentSpecialGrowingProperty
        """
        if value not in cls.MAP:
            for _, v in cls.INSTANCES.iteritems():
                if v.growing_low <= value <= v.growing_high:
                    cls.MAP[value] = v
                    break
            else:
                raise RuntimeError("ConfigEquipmentSpecialGrowingProperty, can not find config for growing: {0}".format(value))

        return cls.MAP[value]

class EquipmentSpecialGenerate(object):
    __slots__ = [
        'id',
        'normal_cost', 'normal_generate',
        'advance_cost', 'advance_generate',
        'minutes'
    ]

    def __init__(self):
        self.id = 0
        self.normal_cost = []
        self.normal_generate = []
        self.advance_cost = []
        self.advance_generate = []
        self.minutes = 0


class ConfigEquipmentSpecialGenerate(ConfigBase):
    EntityClass = EquipmentSpecialGenerate
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: EquipmentSpecialGenerate
        """
        return super(ConfigEquipmentSpecialGenerate, cls).get(_id)

class EquipmentSpecialScoreToGrowing(object):
    __slots__ = [
        'id', 'tp',
        'score_low', 'score_high',
        'growing_low', 'growing_high'
    ]

    def __init__(self):
        self.id = 0
        self.tp = 0
        self.score_low = 0
        self.score_high = 0
        self.growing_low = 0
        self.growing_high = 0


class ConfigEquipmentSpecialScoreToGrowing(ConfigBase):
    EntityClass = EquipmentSpecialScoreToGrowing
    INSTANCES = {}
    """:type: dict[int, EquipmentSpecialScoreToGrowing]"""
    FILTER_CACHE = {}
    MAP = {}

    @classmethod
    def get_random_growing_by_score(cls, tp, value):
        """

        :rtype: int
        """
        key = "{0}.{1}".format(tp, value)

        if key not in cls.MAP:
            for _, v in cls.INSTANCES.iteritems():
                if v.tp == tp and v.score_low <= value <= v.score_high:
                    cls.MAP[key] = v
                    break
            else:
                raise RuntimeError("ConfigEquipmentSpecialScoreToGrowing, can not find config for score: {0}".format(value))

        obj = cls.MAP[key]
        return random.randint(obj.growing_low, obj.growing_high)

class EquipmentSpecialLevel(object):
    __slots__ = ['id', 'items']
    def __init__(self):
        self.id = 0
        self.items = []


class ConfigEquipmentSpecialLevel(ConfigBase):
    EntityClass = EquipmentSpecialLevel
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: EquipmentSpecialLevel
        """
        return super(ConfigEquipmentSpecialLevel, cls).get(_id)