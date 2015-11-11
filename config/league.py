# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       league
Date Created:   2015-09-02 18:21
Description:

"""

from config.base import ConfigBase


class League(object):
    __slots__ = ['id', 'day_reward', 'day_reward_lose', 'week_reward']

    def __init__(self):
        self.id = 0
        self.day_reward = 0
        self.day_reward_lose = 0
        self.week_reward = 0


class ConfigLeague(ConfigBase):
    EntityClass = League
    INSTANCES = {}
    FILTER_CACHE = {}

    MIN_LEVEL = 0
    MAX_LEVEL = 0

    @classmethod
    def initialize(cls, fixture):
        super(ConfigLeague, cls).initialize(fixture)
        levels = cls.INSTANCES.keys()
        cls.MIN_LEVEL = min(levels)
        cls.MAX_LEVEL = max(levels)

    @classmethod
    def get(cls, id):
        """

        :rtype : League
        """
        return super(ConfigLeague, cls).get(id)
