# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       building
Date Created:   2015-07-20 23:14
Description:

"""

from config.base import ConfigBase


class BuildingLevel(object):
    __slots__ = ['level', 'up_condition_value', 'up_need_gold',
                 'up_need_minutes', 'up_need_items',
                 'effect', ]

    def __init__(self):
        self.level = 0
        self.up_condition_value = 0
        self.up_need_gold = 0
        self.up_need_minutes = 0
        self.up_need_items = []
        self.effect = {}

    @classmethod
    def new(cls, **kwargs):
        obj = cls()
        for k in cls.__slots__:
            setattr(obj, k, kwargs[k])

        return obj


class Building(object):
    __slots__ = ['id', 'level_up_condition_type', 'max_levels', 'levels']

    def __init__(self):
        self.id = 0
        self.level_up_condition_type = 0
        self.max_levels = 0
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
    def get(cls, _id):
        """

        :rtype : Building
        """
        return super(ConfigBuilding, cls).get(_id)
