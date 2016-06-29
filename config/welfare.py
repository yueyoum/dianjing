# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       welfare
Date Created:   2016-06-28 14-52
Description:

"""

from config.base import ConfigBase


class SignIn(object):
    __slots__ = ['id', 'reward', 'vip', 'vip_reward']

    def __init__(self):
        self.id = 0
        self.reward = []
        self.vip = 0
        self.vip_reward = []


class ConfigWelfareSignIn(ConfigBase):
    EntityClass = SignIn
    INSTANCES = {}
    FILTER_CACHE = {}

    FIRST_DAY = 0
    LAST_DAY = 0

    @classmethod
    def initialize(cls, fixture):
        super(ConfigWelfareSignIn, cls).initialize(fixture)
        keys = cls.INSTANCES.keys()
        cls.FIRST_DAY = min(keys)
        cls.LAST_DAY = max(keys)

    @classmethod
    def get(cls, _id):
        """

        :rtype: SignIn
        """
        return super(ConfigWelfareSignIn, cls).get(_id)


class NewPlayer(object):
    __slots__ = ['id', 'reward']

    def __init__(self):
        self.id = 0
        self.reward = []


class ConfigWelfareNewPlayer(ConfigBase):
    EntityClass = NewPlayer
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: NewPlayer
        """
        return super(ConfigWelfareNewPlayer, cls).get(_id)


class LevelReward(object):
    __slots__ = ['id', 'reward']

    def __init__(self):
        self.id = 0
        self.reward = []


class ConfigWelfareLevelReward(ConfigBase):
    EntityClass = LevelReward
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: LevelReward
        """
        return super(ConfigWelfareLevelReward, cls).get(_id)
