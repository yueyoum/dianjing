# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       union
Date Created:   2016-07-27 14:57
Description:

"""

from config.base import ConfigBase

class UnionLevel(object):
    __slots__ = ['id', 'contribution', 'members_limit']
    def __init__(self):
        self.id = 0
        self.contribution = 0
        self.members_limit = 0

class UnionSignin(object):
    __slots__ = ['id', 'contribution', 'rewards', 'cost', 'vip']
    def __init__(self):
        self.id = 0
        self.contribution = 0
        self.rewards = []
        self.cost = []
        self.vip = 0


class ConfigUnionLevel(ConfigBase):
    EntityClass = UnionLevel
    INSTANCES = {}
    FILTER_CACHE = {}
    MAX_LEVEL = 0

    @classmethod
    def initialize(cls, fixture):
        super(ConfigUnionLevel, cls).initialize(fixture)
        cls.MAX_LEVEL = max(cls.INSTANCES.keys())

    @classmethod
    def get(cls, _id):
        """

        :rtype: UnionLevel
        """
        return super(ConfigUnionLevel, cls).get(_id)

class ConfigUnionSignin(ConfigBase):
    EntityClass = UnionSignin
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: UnionSignin
        """
        return super(ConfigUnionSignin, cls).get(_id)
