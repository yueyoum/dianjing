# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       tower
Date Created:   2016-05-04 17-58
Description:

"""

import random
from config.base import ConfigBase


class TowerLevel(object):
    __slots__ = [
        'id', 'talent_id', 'staffs',
        'star_reward',
        'turntable'
    ]

    def __init__(self):
        self.id = 0
        self.talent_id = 0
        self.staffs = []
        self.star_reward = {}
        self.turntable = {}

    def get_star_reward(self, star):
        return self.star_reward[str(star)]
    
    def get_turntable(self):
        table = {}
        for k, v in self.turntable:
            table[k] = random.sample(v, 4)
        
        return table


class ConfigTowerLevel(ConfigBase):
    EntityClass = TowerLevel
    INSTANCES = {}
    FILTER_CACHE = {}
    
    @classmethod
    def get(cls, _id):
        """

        :rtype: TowerLevel
        """
        return super(ConfigTowerLevel, cls).get(_id)