# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       active_value
Date Created:   2015-10-09 15:24
Description:

"""

from config.base import ConfigBase


class ActiveReward(object):
    __slots__ = ['id', 'value', 'package']

    def __init__(self):
        self.id = 0
        self.value = 0
        self.package = 0


class ActiveFunction(object):
    __slots__ = ['id', 'function_name', 'value', 'max_times']

    def __init__(self):
        self.id = ''
        self.function_name = ''
        self.value = 0
        self.max_times = 0


class ConfigActiveReward(ConfigBase):
    EntityClass = ActiveReward
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype : ActiveReward
        """
        return super(ConfigActiveReward, cls).get(_id)


class ConfigActiveFunction(ConfigBase):
    EntityClass = ActiveFunction
    INSTANCES = {}
    FILTER_CACHE = {}

    FUNCTION_DICT = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigActiveFunction, cls).initialize(fixture)

        for v in cls.INSTANCES.values():
            cls.FUNCTION_DICT[v.function_name] = v

    @classmethod
    def get(cls, function_name):
        """

        :rtype : ActiveFunction
        """

        return cls.FUNCTION_DICT.get(function_name, None)

    @classmethod
    def all_functions(cls):
        return cls.FUNCTION_DICT.keys()
