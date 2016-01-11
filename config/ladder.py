# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       ladder
Date Created:   2015-08-13 15:29
Description:

"""

from config.base import ConfigBase

class LadderRankReward(object):
    __slots__ = ['id', 'reward_gold', 'reward_score', 'mail_title', 'mail_content']
    def __init__(self):
        self.id = 0
        self.reward_gold = 0
        self.reward_score = 0
        self.mail_title = 0
        self.mail_content = 0


class LadderScoreStore(object):
    __slots__ = ['id', 'times_limit', 'score', 'item', 'item_amount']
    def __init__(self):
        self.id = 0
        self.times_limit = 0
        self.score = 0
        self.item = 0
        self.item_amount = 0

class ConfigLadderRankReward(ConfigBase):
    EntityClass = LadderRankReward
    INSTANCES = {}
    FILTER_CACHE = {}

    RANKS = []
    RANKS_AMOUNT = 0

    @classmethod
    def initialize(cls, fixture):
        super(ConfigLadderRankReward, cls).initialize(fixture)
        cls.RANKS = cls.INSTANCES.values()
        cls.RANKS.sort(key=lambda obj: obj.id)
        cls.RANKS_AMOUNT = len(cls.RANKS)


    @classmethod
    def get(cls, id):
        """

        :rtype : LadderRankReward
        """
        return super(ConfigLadderRankReward, cls).get(id)

    @classmethod
    def get_reward_object(cls, rank):
        """

        :rtype : LadderRankReward
        """
        for i in range(cls.RANKS_AMOUNT):
            if cls.RANKS[i].id > rank:
                return cls.RANKS[i-1]

        return cls.RANKS[-1]


class ConfigLadderScoreStore(ConfigBase):
    EntityClass = LadderScoreStore
    INSTANCES = {}
    FILTER_CACHE = {}
    
    @classmethod
    def get(cls, id):
        """

        :rtype : LadderScoreStore
        """
        return super(ConfigLadderScoreStore, cls).get(id)
