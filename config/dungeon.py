"""
Author:         ouyang
Filename:       dungeon
Date Created:   2016-04-25 20:06
Description:

"""

import random
from config.base import ConfigBase


class Dungeon(object):
    __slots__ = ['id', 'cost', 'open_time', 'map_name']

    def __init__(self):
        self.id = 0
        self.cost = 0
        self.open_time = []
        self.map_name = ''


class ConfigDungeon(ConfigBase):
    EntityClass = Dungeon
    INSTANCES = {}
    """:type: dict[int, Dungeon]"""
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: Dungeon
        """
        return super(ConfigDungeon, cls).get(_id)


class DungeonGrade(object):
    __slots__ = ['id', 'name', 'belong', 'need_level', 'drop', 'npc']

    def __init__(self):
        self.id = 0
        self.name = ""
        self.belong = 0
        self.need_level = 0
        self.drop = []
        self.npc = 0

    def get_drop(self):
        drop = []
        for _id, _amount, _prob in self.drop:
            if _prob >= random.randint(1, 100):
                drop.append((_id, _amount))

        return drop


class ConfigDungeonGrade(ConfigBase):
    EntityClass = DungeonGrade
    INSTANCES = {}
    """:type: dict[int, DungeonGrade]"""
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: DungeonGrade
        """
        return super(ConfigDungeonGrade, cls).get(_id)


class ResetCost(object):
    __slots__ = ['id', 'times']
    def __init__(self):
        self.id = 0
        self.times = []

    def get_cost(self, times):
        for t, cost in self.times:
            if times >= t:
                return cost

        raise RuntimeError("ConfigDungeonBuyCost Error times: {0}".format(times))


class ConfigDungeonBuyCost(ConfigBase):
    EntityClass = ResetCost
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get_cost(cls, dungeon_id, times):
        return cls.INSTANCES[dungeon_id].get_cost(times)
