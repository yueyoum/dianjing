# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       skill
Date Created:   2015-07-24 11:21
Description:

"""

from config.base import ConfigBase

class Skill(object):
    __slots__ = ['id', 'race', 'type_id', 'addition_ids',
                 'value_base', 'level_grow', 'max_level',
                 'levels',
                 ]
    
    def __init__(self):
        self.id = 0
        self.race = 0
        self.type_id = 0
        self.addition_ids = []
        self.value_base = 0
        self.level_grow = 0
        self.max_level = 0
        self.levels = {}

class SkillWashCost(object):
    __slots__ = ['id', 'cost_type', 'cost_value']
    def __init__(self):
        self.id = 0
        self.cost_type = 0
        self.cost_value = 0


class ConfigSkill(ConfigBase):
    EntityClass = Skill
    INSTANCES = {}
    FILTER_CACHE = {}

    SHOP_SKILL_ID = 0
    BROADCAST_SKILL_ID = 0
    SPONSOR_SKILL_ID = 0

    @classmethod
    def initialize(cls, fixture):
        super(ConfigSkill, cls).initialize(fixture)
        for k, v in cls.INSTANCES.iteritems():
            addition_ids = []
            for item in v.addition_ids:
                addition_ids.append((item['key'], item['value']))

            v.addition_ids = addition_ids

            if v.type_id == 1:
                cls.SHOP_SKILL_ID = k
            elif v.type_id == 3:
                cls.BROADCAST_SKILL_ID = k
            elif v.type_id == 4:
                cls.SPONSOR_SKILL_ID = k

    @classmethod
    def get(cls, id):
        """

        :rtype : Skill
        """
        return super(ConfigSkill, cls).get(id)


class ConfigSkillWashCost(ConfigBase):
    EntityClass = SkillWashCost
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get_cost(cls, locked_skill_amount):
        """

        :rtype : dict
        """
        obj = cls.INSTANCES[locked_skill_amount]
        if obj.cost_type == 1:
            return {'gold': -obj.cost_value}
        return {'diamond': -obj.cost_value}



class TalentSkill(object):
    __slots__ = [
        'id', 'target',
        'staff_attack', 'staff_attack_percent',
        'staff_defense', 'staff_defense_percent',
        'staff_manage', 'staff_manage_percent',
        'staff_operation', 'staff_operation_percent',

        'unit_hp_percent', 'unit_attack_percent', 'unit_defense_percent',
        'unit_hit_rate', 'unit_dodge_rate', 'unit_crit_rate',
        'unit_toughness_rate', 'unit_crit_multiple',

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
        self.target = 0
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

        self.unit_final_hurt_addition = 0
        self.unit_final_hurt_reduce = 0


class ConfigTalentSkill(ConfigBase):
    EntityClass = TalentSkill
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        # type: (int) -> TalentSkill
        return super(ConfigTalentSkill, cls).get(_id)