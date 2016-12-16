# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       championship
Date Created:   2016-12-08 16:11
Description:

"""

from config.base import ConfigBase

class WinScore(object):
    __slots__ = ['id', 'score']
    def __init__(self):
        self.id = 0
        self.score = 0

class ConfigChampionWinScore(ConfigBase):
    EntityClass = WinScore
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: WinScore
        """
        return super(ConfigChampionWinScore, cls).get(_id)

class ScoreReward(object):
    __slots__ = ['id', 'mail_title', 'mail_content', 'reward']
    def __init__(self):
        self.id = 0
        self.mail_title = ''
        self.mail_content = ''
        self.reward = []

class RankReward(object):
    __slots__ = ['id', 'mail_title', 'mail_content', 'reward']
    def __init__(self):
        self.id = 0
        self.mail_title = ''
        self.mail_content = ''
        self.reward = []


class ConfigChampionScoreReward(ConfigBase):
    EntityClass = ScoreReward
    INSTANCES = {}
    FILTER_CACHE = {}

    LIST = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigChampionScoreReward, cls).initialize(fixture)
        cls.LIST = cls.INSTANCES.items()
        cls.LIST.sort(key=lambda item: item[0], reverse=True)

    @classmethod
    def get_by_score(cls, score):
        """

        :rtype: ScoreReward | None
        """
        for k, v in cls.LIST:
            if score >= k:
                return v

        return None


class ConfigChampionRankReward(ConfigBase):
    EntityClass = RankReward
    INSTANCES = {}
    FILTER_CACHE = {}

    LIST = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigChampionRankReward, cls).initialize(fixture)
        cls.LIST = cls.INSTANCES.items()
        cls.LIST.sort(key=lambda item: item[0], reverse=True)

    @classmethod
    def get(cls, _id):
        """

        :rtype: RankReward
        """
        return super(ConfigChampionRankReward, cls).get(_id)


class Bet(object):
    __slots__ = ['id', 'level', 'cost',
                 'win_mail_title', 'win_mail_content', 'win_reward',
                 'lose_mail_title', 'lose_mail_content', 'lose_reward']

    def __init__(self):
        self.id = 0
        self.level = 0
        self.cost = []
        self.win_mail_title = ''
        self.win_mail_content = ''
        self.win_reward = []
        self.lose_mail_title = ''
        self.lose_mail_content = ''
        self.lose_reward = []

class ConfigChampionBet(ConfigBase):
    EntityClass = Bet
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: Bet
        """
        return super(ConfigChampionBet, cls).get(_id)