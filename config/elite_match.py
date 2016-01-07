# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       elite_match
Date Created:   2015-12-10 11:21
Description:

"""

from config.base import ConfigBase


class EliteArea(object):
    __slots__ = ['id', 'match_ids', 'need_club_level', 'star_reward']

    def __init__(self):
        self.id = 0
        self.match_ids = []
        self.need_club_level = 0
        self.star_reward = []

    def first_match_id(self):
        return self.match_ids[0]

    def last_match_id(self):
        return self.match_ids[-1]

    def next_match_id(self, mid):
        index = self.match_ids.index(mid)
        try:
            return self.match_ids[index + 1]
        except IndexError:
            return 0


class EliteMatch(object):
    __slots__ = [
        'id', 'max_times', 'club_flag', 'name', 'club_name', 'policy',
        'staff_level', 'staffs', 'reward',
        'area_id',
    ]

    def __init__(self):
        self.id = 0
        self.max_times = 0
        self.club_flag = 0
        self.name = ""
        self.club_name = ""
        self.policy = 0
        self.staff_level = 0
        self.staffs = []
        self.reward = 0
        self.area_id = 0


class ConfigEliteArea(ConfigBase):
    EntityClass = EliteArea
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def post_fix(cls):
        for k, v in cls.INSTANCES.iteritems():
            for mid in v.match_ids:
                ConfigEliteMatch.get(mid).area_id = k

    @classmethod
    def get(cls, _id):
        """

        :rtype : EliteArea
        """
        return super(ConfigEliteArea, cls).get(_id)

    @classmethod
    def next_area_id(cls, aid):
        ids = cls.INSTANCES.keys()
        ids.sort()

        index = ids.index(aid)
        try:
            return ids[index + 1]
        except IndexError:
            return 0


class ConfigEliteMatch(ConfigBase):
    EntityClass = EliteMatch
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype : EliteMatch
        """
        return super(ConfigEliteMatch, cls).get(_id)
