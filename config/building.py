# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       building
Date Created:   2015-07-20 23:14
Description:

"""

from config.base import ConfigBase

class BuildingLevel(object):
    __slots__ = ['level', 'up_need_club_level', 'up_need_gold', 'value1']
    def __init__(self):
        self.level = None
        self.up_need_club_level = None
        self.up_need_gold = None
        self.value1 = None

    @classmethod
    def new(cls, **kwargs):
        obj = cls()
        for k in cls.__slots__:
            setattr(obj, k, kwargs[k])

        return obj


class Building(object):
    __slots__ = ['id', 'max_levels', 'levels']

    def __init__(self):
        self.id = None
        self.max_levels = None
        self.levels = {}

    def get_level(self, lv):
        """

        :rtype : BuildingLevel
        """
        return self.levels[lv]


class ConfigBuilding(ConfigBase):
    EntityClass = Building
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigBuilding, cls).initialize(fixture)
        for v in cls.INSTANCES.values():
            levels = {}
            for lv, data in v.levels.iteritems():
                data['level'] = int(lv)
                levels[int(lv)] = BuildingLevel.new(**data)

            v.levels = levels


    @classmethod
    def get(cls, id):
        """

        :rtype : Building
        """
        return super(ConfigBuilding, cls).get(id)

    @classmethod
    def can_level_up_building_ids(cls):
        res = []
        for k, v in cls.INSTANCES.iteritems():
            if v.max_levels:
                res.append(int(k))

        return res

