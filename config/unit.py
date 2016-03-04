# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       unit
Date Created:   2015-07-15 16:01
Description:

"""


from config.base import ConfigBase

class Unit(object):
    __slots__ = [
        'id', 'race',
        'first_trig', 'second_trig', 'third_trig',
        'skill',
        'des'
    ]

    def __init__(self):
        self.id = None
        self.race = None
        self.first_trig = None
        self.second_trig = None
        self.third_trig = None
        self.skill = None
        self.des = None


class UnitNew(object):
    __slots__ = [
        'id', 'tp', 'race', 'attack_tp', 'defense_tp', 'cost',
        'skill_1', 'skill_2',
        'hp_max_base', 'attack_base', 'defense_base',
        'attack_speed_base', 'attack_range_base', 'move_speed_base',
        'hit_rate', 'dodge_rate', 'crit_rate', 'toughness_rate',
        'crit_multiple',
        'hurt_addition_to_terran',
        'hurt_addition_to_protoss',
        'hurt_addition_to_zerg',
        'hurt_addition_by_terran',
        'hurt_addition_by_protoss',
        'hurt_addition_by_zerg',
        'final_hurt_addition',
        'final_hurt_reduce',
    ]

    def __init__(self):
        self.id = 0
        self.tp = 0
        self.race = 0
        self.attack_tp = 0
        self.defense_tp = 0
        self.cost = 0
        self.skill_1 = 0
        self.skill_2 = 0
        self.hp_max_base = 0
        self.attack_base = 0
        self.defense_base = 0
        self.attack_speed_base = 0
        self.attack_range_base = 0
        self.move_speed_base = 0
        self.hit_rate = 0
        self.dodge_rate = 0
        self.crit_rate = 0
        self.toughness_rate = 0
        self.crit_multiple = 0
        self.hurt_addition_to_terran = 0
        self.hurt_addition_to_protoss = 0
        self.hurt_addition_to_zerg = 0
        self.hurt_addition_by_terran = 0
        self.hurt_addition_by_protoss = 0
        self.hurt_addition_by_zerg = 0
        self.final_hurt_addition = 0
        self.final_hurt_reduce = 0



class ConfigUnit(ConfigBase):
    EntityClass = Unit
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, id):
        """

        :rtype : Unit
        """
        return super(ConfigUnit, cls).get(id)


class ConfigUnitNew(ConfigBase):
    EntityClass = UnitNew
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: UnitNew
        """
        return super(ConfigUnitNew, cls).get(_id)


class Policy(object):
    __slots__ = [
        'id', 'name', 'advantage_add_round', 'advantage_add_value'
    ]

    def __init__(self):
        self.id = None                          # 战术ID
        self.name = None                        # 战术名
        self.advantage_add_round = None         # 加成轮次
        self.advantage_add_value = None         # 加成值


class ConfigPolicy(ConfigBase):
    EntityClass = Policy
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, id):
        """

        :rtype : Policy
        """
        return super(ConfigPolicy, cls).get(id)


