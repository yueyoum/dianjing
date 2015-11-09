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

    def get_upgrade_needs(self, level):
        needs = self.levels[str(level)]
        return needs['upgrade_training_id'], needs['upgrade_training_amount']


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
