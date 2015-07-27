# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       unit
Date Created:   2015-07-15 16:01
Description:

"""


from config.base import ConfigBase

class Unit(object):
    __slots__ = [
        'id', 'race',
        'first_trig', 'second_trig', 'third_trig',
        'des'
    ]

    def __init__(self):
        self.id = None
        self.race = None
        self.first_trig = None
        self.second_trig = None
        self.third_trig = None
        self.des = None


class ConfigUnit(ConfigBase):
    EntityClass = Unit
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, id):
        """

        :rtype : Unit
        """
        return super(ConfigUnit, cls).get(id)


class Policy(object):
    __slots__ = [
        'id', 'name', 'advantage_add_round', 'advantage_add_value'
    ]

    def __init__(self):
        self.id = None                          # 战术ID
        self.name = None                        # 战术名
        self.advantage_add_round = None         # 加成轮次
        self.advantage_add_value = None         # 加成值


class ConfigPolicy(ConfigBase):
    EntityClass = Policy
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, id):
        """

        :rtype : Unit
        """
        return super(ConfigPolicy, cls).get(id)

    @classmethod
    def check(cls, id):
        """

        :param id:
        :return:
        """
        return super(ConfigPolicy, cls).check(id)


