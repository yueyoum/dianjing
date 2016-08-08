# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       activity
Date Created:   2016-08-05 16:42
Description:

"""

from config.base import ConfigBase

class NewPlayer(object):
    __slots__ = ['id', 'day', 'condition_id', 'condition_value', 'rewards']
    def __init__(self):
        self.id = 0
        self.day = 0
        self.condition_id = 0
        self.condition_value = 0
        self.rewards = []


class DailyBuy(object):
    __slots__ = ['id', 'items', 'diamond_now']
    def __init__(self):
        self.id = 0
        self.items = []
        self.diamond_now = 0

class ConfigActivityNewPlayer(ConfigBase):
    EntityClass = NewPlayer
    INSTANCES = {}
    FILTER_CACHE = {}

    CONDITION_ACTIVITY_TABLE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigActivityNewPlayer, cls).initialize(fixture)
        for k, v in cls.INSTANCES.iteritems():
            if v.condition_id in cls.CONDITION_ACTIVITY_TABLE:
                cls.CONDITION_ACTIVITY_TABLE[v.condition_id].append(k)
            else:
                cls.CONDITION_ACTIVITY_TABLE[v.condition_id] = [k]

    @classmethod
    def get(cls, _id):
        """

        :rtype: NewPlayer
        """
        return super(ConfigActivityNewPlayer, cls).get(_id)

    @classmethod
    def get_activity_ids_by_condition_id(cls, con_id):
        return cls.CONDITION_ACTIVITY_TABLE.get(con_id, [])

class ConfigActivityDailyBuy(ConfigBase):
    EntityClass = DailyBuy
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: DailyBuy
        """
        return super(ConfigActivityDailyBuy, cls).get(_id)