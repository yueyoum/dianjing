"""
Author:         ouyang
Filename:       dungeon
Date Created:   2016-04-25 20:06
Description:

"""
from config.base import ConfigBase


class Dungeon(object):
    __slots__ = ['id', 'cost', 'open_time']

    def __init__(self):
        self.id = 0
        self.cost = 0
        self.open_time = []


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
    __slots__ = ['id', 'belong', 'need_level', 'drop']

    def __init__(self):
        self.id = 0
        self.belong = 0
        self.need_level = 0
        self.drop = []


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