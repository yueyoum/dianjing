# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training
Date Created:   2015-07-21 00:15
Description:

"""

from config.base import ConfigBase

class Training(object):
    __slots__ = [
        'id', 'building', 'need_building_level', 'tp',
        'cost_type', 'cost_value', 'minutes',
        'package',
        'skill_id', 'skill_level',
    ]
    
    def __init__(self):
        self.id = 0
        self.building = 0
        self.need_building_level = 0
        self.tp = 0
        self.cost_type = 0
        self.cost_value = 0
        self.minutes = 0
        self.package = 0
        self.skill_id = 0
        self.skill_level = 0


class ConfigTraining(ConfigBase):
    EntityClass = Training
    INSTANCES = {}
    FILTER_CACHE = {}
    
    @classmethod
    def get(cls, id):
        """

        :rtype : Training
        """
        return super(ConfigTraining, cls).get(id)

