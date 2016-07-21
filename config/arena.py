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
    __slots__ = ['id', 'score_low', 'score_high', 'npcs', 'amount']

    def __init__(self):
        self.id = 0
        self.npcs = []
        self.score_low = 0
        self.score_high = 0
        self.amount = 0

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

class RankRewardWeekly(object):
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
            prob = random.randint(1, 100)
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


class SearchResetCost(object):
    __slots__ = ['id', 'diamond']
    def __init__(self):
        self.id = 0
        self.diamond = 0


class SearchRange(object):
    __slots__ = ['id', 'range_1', 'range_2', 'score_win', 'score_lose']
    def __init__(self):
        self.id = 0
        self.range_1 = 0
        self.range_2 = 0
        self.score_win = 0
        self.score_lose = 0


class ConfigArenaNPC(ConfigBase):
    EntityClass = ArenaNPC
    INSTANCES = {}
    """:type: dict[int, ArenaNPC]"""
    FILTER_CACHE = {}


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

    LIST = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigArenaRankReward, cls).initialize(fixture)
        cls.LIST = cls.INSTANCES.items()
        cls.LIST.sort(key=lambda item: item[0], reverse=True)

    @classmethod
    def get(cls, rank):
        """

        :rtype: RankReward
        """
        for k, v in cls.LIST:
            if rank >= k:
                return v

        raise RuntimeError("ConfigArenaRankReward, Error rank: {0}".format(rank))

class ConfigArenaRankRewardWeekly(ConfigBase):
    EntityClass = RankRewardWeekly
    INSTANCES = {}
    FILTER_CACHE = {}

    LIST = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigArenaRankRewardWeekly, cls).initialize(fixture)
        cls.LIST = cls.INSTANCES.items()
        cls.LIST.sort(key=lambda item: item[0], reverse=True)

    @classmethod
    def get(cls, rank):
        """

        :rtype: RankRewardWeekly
        """
        for k, v in cls.LIST:
            if rank >= k:
                return v

        raise RuntimeError("ConfigArenaRankRewardWeekly, Error rank: {0}".format(rank))


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


class ConfigArenaSearchRange(ConfigBase):
    EntityClass = SearchRange
    INSTANCES = {}
    """:type: dict[int, SearchRange]"""
    FILTER_CACHE = {}

    LIST = []
    """:type: list[SearchRange]"""
    START_INDEX = 0
    MAX_INDEX = 0

    @classmethod
    def initialize(cls, fixture):
        super(ConfigArenaSearchRange, cls).initialize(fixture)
        cls.LIST = cls.INSTANCES.values()
        cls.LIST.sort(key=lambda item: item.id)

        cls.MAX_INDEX = len(cls.LIST) - 1

        for index, i in enumerate(cls.LIST):
            if i.range_1 <= 1 <= i.range_2:
                cls.START_INDEX = index
                break
        else:
            raise RuntimeError("ConfigArenaSearchRange Can not find StartIndex")

    @classmethod
    def get(cls, index):
        return cls.LIST[index]


class ConfigArenaSearchResetCost(ConfigBase):
    EntityClass = SearchResetCost
    INSTANCES = {}
    FILTER_CACHE = {}

    LIST = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigArenaSearchResetCost, cls).initialize(fixture)
        for k, v in cls.INSTANCES.iteritems():
            cls.LIST.append((k, v.diamond))

        cls.LIST.sort(key=lambda item: item[0], reverse=True)

    @classmethod
    def get_cost(cls, times):
        for k, v in cls.LIST:
            if times >= k:
                return v

        raise RuntimeError("ConfigArenaSearchResetCost, Error times: {0}".format(times))
