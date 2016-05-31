# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       arena
Date Created:   2016-04-29 10-45
Description:

"""

import random
from config.base import ConfigBase

class ArenaNPC(object):
    __slots__ = ['id', 'npcs']

    def __init__(self):
        self.id = 0
        self.npcs = []

    def get_npc_id(self):
        return random.choice(self.npcs)

class HonorReward(object):
    __slots__ = ['id', 'reward']
    def __init__(self):
        self.id = 0
        self.reward = []

class RankReward(object):
    __slots__ = ['id', 'reward', 'mail_title', 'mail_content']
    def __init__(self):
        self.id = 0
        self.reward = []
        self.mail_title = ""
        self.mail_content = ""

class MatchReward(object):
    __slots__ = ['id', 'honor', 'item_id', 'item_amount', 'random_items']
    def __init__(self):
        self.id = 0
        self.honor = 0
        self.item_id = 0
        self.item_amount = 0
        self.random_items = []

    def get_drop(self):
        assert self.item_id
        items = {
            self.item_id: self.item_amount
        }

        if self.random_items:
            prob = random.randint(1, self.random_items[-1][2])
            for _id, _amount, _prob in self.random_items:
                if _prob >= prob:
                    if _id in items:
                        items[_id] += _amount
                    else:
                        items[_id] = _amount

                    break

        return items.items()

class BuyTimesCost(object):
    __slots__ = ['id', 'diamond']
    def __init__(self):
        self.id = 0
        self.diamond = 0


class ConfigArenaNPC(ConfigBase):
    EntityClass = ArenaNPC
    INSTANCES = {}
    FILTER_CACHE = {}

    ORDERED_INSTANCES = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigArenaNPC, cls).initialize(fixture)

        cls.ORDERED_INSTANCES = cls.INSTANCES.items()
        cls.ORDERED_INSTANCES.sort(key=lambda item: item[0], reverse=True)

    @classmethod
    def get(cls, _id):
        """

        :rtype: ArenaNPC
        """
        # 这个方法只会在 初始化竞技场的时候 调用
        for a, b in cls.ORDERED_INSTANCES:
            if _id >= a:
                return b

class ConfigArenaHonorReward(ConfigBase):
    EntityClass = HonorReward
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: HonorReward
        """
        return super(ConfigArenaHonorReward, cls).get(_id)

class ConfigArenaRankReward(ConfigBase):
    EntityClass = RankReward
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: RankReward
        """
        return super(ConfigArenaRankReward, cls).get(_id)

class ConfigArenaMatchReward(ConfigBase):
    EntityClass = MatchReward
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: MatchReward
        """
        return super(ConfigArenaMatchReward, cls).get(_id)


class ConfigArenaBuyTimesCost(ConfigBase):
    EntityClass = BuyTimesCost
    INSTANCES = {}
    FILTER_CACHE = {}

    LIST = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigArenaBuyTimesCost, cls).initialize(fixture)
        for k, v in cls.INSTANCES.iteritems():
            cls.LIST.append((k, v.diamond))

        cls.LIST.sort(key=lambda item: item[0], reverse=True)

    @classmethod
    def get_cost(cls, times):
        for k, v in cls.LIST:
            if times >= k:
                return v

        raise RuntimeError("ConfigArenaBuyTimesCost, Error times: {0}".format(times))
