# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       union
Date Created:   2016-07-27 14:57
Description:

"""

import random
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


class UnionExplore(object):
    __slots__ = ['id', 'staffs', 'explore_reward', 'harass_reward']

    def __init__(self):
        self.id = 0
        self.staffs = []
        self.explore_reward = []
        self.harass_reward = []


class ConfigUnionExplore(ConfigBase):
    EntityClass = UnionExplore
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get_staff_id(cls):
        return random.choice(cls.INSTANCES[1].staffs)

    @classmethod
    def get_explore_reward(cls):
        reward = random.choice(cls.INSTANCES[1].explore_reward)
        return [reward]

    @classmethod
    def get_harass_reward(cls):
        reward = random.choice(cls.INSTANCES[1].harass_reward)
        return [reward]


class UnionExploreRankReward(object):
    __slots__ = ['id', 'reward', 'mail_title', 'mail_content']

    def __init__(self):
        self.id = 0
        self.reward = []
        self.mail_title = ''
        self.mail_content = ''


class ConfigUnionExploreRankReward(ConfigBase):
    EntityClass = UnionExploreRankReward
    INSTANCES = {}
    FILTER_CACHE = {}

    LIST = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigUnionExploreRankReward, cls).initialize(fixture)
        cls.LIST = cls.INSTANCES.items()
        cls.LIST.sort(key=lambda item: item[0], reverse=True)

    @classmethod
    def get_by_rank(cls, rank):
        """

        :rtype: UnionExploreRankReward | None
        """
        for k, v in cls.LIST:
            if rank >= k:
                return v

        return None


class UnionMemberExploreRankReward(object):
    __slots__ = ['id', 'reward', 'mail_title', 'mail_content']

    def __init__(self):
        self.id = 0
        self.reward = []
        self.mail_title = ''
        self.mail_content = ''


class ConfigUnionMemberExploreRankReward(ConfigBase):
    EntityClass = UnionMemberExploreRankReward
    INSTANCES = {}
    FILTER_CACHE = {}

    LIST = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigUnionMemberExploreRankReward, cls).initialize(fixture)
        cls.LIST = cls.INSTANCES.items()
        cls.LIST.sort(key=lambda item: item[0], reverse=True)

    @classmethod
    def get_by_rank(cls, rank):
        """

        :rtype: UnionMemberExploreRankReward | None
        """
        for k, v in cls.LIST:
            if rank >= k:
                return v

        return None


class UnionHarassBuyTimesCost(object):
    __slots__ = ['id', 'diamond']

    def __init__(self):
        self.id = 0
        self.diamond = 0


class ConfigUnionHarassBuyTimesCost(ConfigBase):
    EntityClass = UnionHarassBuyTimesCost
    INSTANCES = {}
    FILTER_CACHE = {}

    LIST = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigUnionHarassBuyTimesCost, cls).initialize(fixture)
        for k, v in cls.INSTANCES.iteritems():
            cls.LIST.append((k, v.diamond))

        cls.LIST.sort(key=lambda item: item[0], reverse=True)

    @classmethod
    def get_cost(cls, times):
        for k, v in cls.LIST:
            if times >= k:
                return v

        raise RuntimeError("ConfigUnionHarassBuyTimesCost, Error times: {0}".format(times))


class UnionSkillLevel(object):
    __slots__ = ['cost', 'talent_id']

    def __init__(self):
        self.cost = []
        self.talent_id = 0

    @classmethod
    def create(cls, data):
        obj = cls()
        obj.cost = data['cost']
        obj.talent_id = data['talent_id']
        return obj


class UnionSkill(object):
    __slots__ = ['id', 'max_level', 'levels']

    def __init__(self):
        self.id = 0
        self.max_level = 0
        self.levels = {}
        """:type: dict[int, UnionSkillLevel]"""


class ConfigUnionSkill(ConfigBase):
    EntityClass = UnionSkill
    INSTANCES = {}
    """:type: dict[int, UnionSkill]"""
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigUnionSkill, cls).initialize(fixture)
        for k, v in cls.INSTANCES.iteritems():
            v.levels = {int(lv): UnionSkillLevel.create(lv_data) for lv, lv_data in v.levels.iteritems()}

    @classmethod
    def get(cls, _id):
        """

        :rtype: UnionSkill
        """
        return super(ConfigUnionSkill, cls).get(_id)
