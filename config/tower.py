# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       tower
Date Created:   2016-05-04 17-58
Description:

"""

import random

from core.abstract import AbstractClub, AbstractStaff
from config.base import ConfigBase

class _Staff(AbstractStaff):
    __slots__ = []
    def __init__(self, _id):
        super(_Staff, self).__init__()
        self.id = str(_id)
        self.oid = _id
        self.after_init()

class _Club(AbstractClub):
    __slots__ = ['npc_staffs']
    def __init__(self, _id, npc_staffs):
        super(_Club, self).__init__()
        self.id = _id
        self.flag = 1
        self.npc_staffs = npc_staffs

    def load_staffs(self, **kwargs):
        from core.unit import NPCUnit
        for pos, staff_id, unit_id in self.npc_staffs:
            s = _Staff(staff_id)
            s.formation_position = pos
            u = NPCUnit(unit_id, 0, 1)
            s.set_unit(u)
            s.calculate()
            self.formation_staffs.append(s)


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
        if not self.turntable['3']:
            return table

        for k, v in self.turntable.iteritems():
            table[str(k)] = random.sample(v, 3)
        
        return table

    def make_club(self):
        """

        :rtype: _Club
        """
        return _Club(self.id, self.staffs)


class ResetCost(object):
    __slots__ = ['id', 'cost']
    def __init__(self):
        self.id = 0
        self.cost = 0


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


class ConfigTowerResetCost(ConfigBase):
    EntityClass = ResetCost
    INSTANCES = {}
    FILTER_CACHE = {}

    MAX_KEY = 0

    @classmethod
    def initialize(cls, fixture):
        super(ConfigTowerResetCost, cls).initialize(fixture)
        cls.MAX_KEY = max(cls.INSTANCES.keys())


    @classmethod
    def get(cls, _id):
        """

        :rtype: ResetCost
        """

        x = super(ConfigTowerResetCost, cls).get(_id)
        if not x:
            x = cls.INSTANCES[cls.MAX_KEY]

        return x
