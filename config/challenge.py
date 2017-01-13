# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2015-07-15 10:36
Description:

"""
import random
from config.base import ConfigBase


class Chapter(object):
    __slots__ = [
        'id', 'tp', 'star_reward', 'map_name',
    ]

    def __init__(self):
        self.id = 0
        self.tp = 0
        self.star_reward = []
        self.map_name = ''


class ChallengeMatch(object):
    __slots__ = [
        'id', 'chapter', 'name', 'club_flag', 'energy', 'club_exp', 'staffs', 'drop',
        'condition_challenge', 'times_limit', 'next',
    ]

    def __init__(self):
        self.id = 0
        self.chapter = 0
        self.name = ""
        self.club_flag = ""
        self.energy = 0
        self.club_exp = 0
        self.staffs = ""
        self.drop = ""
        self.condition_challenge = 0
        self.times_limit = 0
        self.next = []

    def get_drop(self, drop_times):
        from core.resource import CLUB_EXP_ITEM_ID

        # 配置表里 club_exp 是分开的
        # 这里把它统一到 drop 里
        drop = {CLUB_EXP_ITEM_ID: self.club_exp}

        for _id, _amount, _p0, _p1 in self.drop:
            str_id = str(_id)

            prob = _p0 + drop_times.get(str_id, 0) * _p1
            if prob >= random.randint(1, 100):

                if _id in drop:
                    drop[_id] += _amount
                else:
                    drop[_id] = _amount

                drop_times[str_id] = 0
            else:
                if str(_id) in drop_times:
                    drop_times[str_id] += 1
                else:
                    drop_times[str_id] = 1

        return drop.items()


class ResetCost(object):
    __slots__ = ['id', 'diamond']
    def __init__(self):
        self.id = 0
        self.diamond  =0


class ConfigChapter(ConfigBase):
    EntityClass = Chapter
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: Chapter
        """
        return super(ConfigChapter, cls).get(_id)

class ConfigChallengeMatch(ConfigBase):
    EntityClass = ChallengeMatch
    INSTANCES = {}
    """:type: dict[int, ChallengeMatch]"""
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype : ChallengeMatch
        """
        return super(ConfigChallengeMatch, cls).get(_id)


class ConfigChallengeResetCost(ConfigBase):
    EntityClass = ResetCost
    INSTANCES = {}
    """:type: dict[int, ResetCost]"""
    FILTER_CACHE = {}

    LIST = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigChallengeResetCost, cls).initialize(fixture)
        for k, v in cls.INSTANCES.iteritems():
            cls.LIST.append((k, v.diamond))

        cls.LIST.sort(key=lambda item: item[0], reverse=True)

    @classmethod
    def get_cost(cls, times):
        for k, v in cls.LIST:
            if times >= k:
                return v

        raise RuntimeError("ConfigChallengeResetCost, Error times: {0}".format(times))