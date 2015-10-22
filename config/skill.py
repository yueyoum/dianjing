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


class ConfigSkill(ConfigBase):
    EntityClass = Skill
    INSTANCES = {}
    FILTER_CACHE = {}
    
    @classmethod
    def get(cls, id):
        """

        :rtype : Skill
        """
        return super(ConfigSkill, cls).get(id)


