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

class OnlineTimeActivity(object):
    __slots__ = ['id', 'rewards']
    def __init__(self):
        self.id = 0
        self.rewards = []

class ChallengeActivity(object):
    __slots__ = ['id', 'rewards']
    def __init__(self):
        self.id = 0
        self.rewards = []

class PurchaseContinues(object):
    __slots__ = ['id', 'rewards']
    def __init__(self):
        self.id = 0
        self.rewards = []

class LevelGrowing(object):
    __slots__ = ['id', 'rewards']
    def __init__(self):
        self.id = 0
        self.rewards = []


class ConfigActivityOnlineTime(ConfigBase):
    EntityClass = OnlineTimeActivity
    INSTANCES = {}
    FILTER_CACHE = {}

    IDS = []
    MIN_ID = 0
    MAX_ID = 0

    @classmethod
    def initialize(cls, fixture):
        super(ConfigActivityOnlineTime, cls).initialize(fixture)
        cls.IDS = cls.INSTANCES.keys()
        cls.MIN_ID = min(cls.IDS)
        cls.MAX_ID = max(cls.IDS)

    @classmethod
    def get(cls, _id):
        """

        :rtype: OnlineTimeActivity
        """
        return super(ConfigActivityOnlineTime, cls).get(_id)

    @classmethod
    def find_next_id(cls, _id):
        index = cls.IDS.index(_id)
        if index == len(cls.IDS) - 1:
            return 0

        return cls.IDS[index+1]


class ConfigActivityChallenge(ConfigBase):
    EntityClass = ChallengeActivity
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: ChallengeActivity
        """
        return super(ConfigActivityChallenge, cls).get(_id)


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


class ConfigActivityPurchaseContinues(ConfigBase):
    EntityClass = PurchaseContinues
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: PurchaseContinues
        """
        return super(ConfigActivityPurchaseContinues, cls).get(_id)


class ConfigActivityLevelGrowing(ConfigBase):
    EntityClass = LevelGrowing
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: LevelGrowing
        """
        return super(ConfigActivityLevelGrowing, cls).get(_id)
