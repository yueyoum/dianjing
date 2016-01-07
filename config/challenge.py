# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2015-07-15 10:36
Description:

"""

from config.base import ConfigBase


class ChallengeType(object):
    __slots__ = [
        'id', 'level', 'condition_challenge_id', 'star_reward'
    ]

    def __init__(self):
        self.id = 0
        self.level = 0
        self.condition_challenge_id = 0
        self.star_reward = []


class ChallengeMatch(object):
    __slots__ = [
        'id', 'need_club_level', 'tp', 'policy', 'level', 'strength', 'staffs', 'package',
        'club_name', 'club_flag', 'max_times',
    ]

    def __init__(self):
        self.id = 0
        self.need_club_level = 0
        self.tp = 0
        self.policy = 0
        self.level = 0
        self.strength = 0
        self.staffs = 0
        self.package = 0
        self.club_name = 0
        self.club_flag = 0
        self.max_times = 0


class ConfigChallengeType(ConfigBase):
    EntityClass = ChallengeType
    INSTANCES = {}
    FILTER_CACHE = {}

    AREA_START_CHALLENGE_ID = {}
    AREA_END_CHALLENGE_ID = {}

    AREA_OPENED_BY_CHALLENGE_ID = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigChallengeType, cls).initialize(fixture)

        for k, v in cls.INSTANCES.iteritems():
            challenge_id = v.condition_challenge_id
            if challenge_id not in cls.AREA_OPENED_BY_CHALLENGE_ID:
                cls.AREA_OPENED_BY_CHALLENGE_ID[challenge_id] = [k]
            else:
                cls.AREA_OPENED_BY_CHALLENGE_ID[challenge_id].append(k)

    @classmethod
    def get(cls, id):
        """

        :rtype : ChallengeType
        """
        return super(ConfigChallengeType, cls).get(id)

    @classmethod
    def start_challenge_id(cls, area_id):
        return cls.AREA_START_CHALLENGE_ID[area_id]

    @classmethod
    def end_challenge_id(cls, area_id):
        return cls.AREA_END_CHALLENGE_ID[area_id]

    @classmethod
    def opened_area_ids(cls, challenge_id):
        return cls.AREA_OPENED_BY_CHALLENGE_ID.get(challenge_id, [])


class ConfigChallengeMatch(ConfigBase):
    EntityClass = ChallengeMatch
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigChallengeMatch, cls).initialize(fixture)

        area_ids = ConfigChallengeType.INSTANCES.keys()
        for i in area_ids:
            this_challenge_ids = cls.filter(tp=i).keys()
            if this_challenge_ids:
                ConfigChallengeType.AREA_START_CHALLENGE_ID[i] = min(this_challenge_ids)
                ConfigChallengeType.AREA_END_CHALLENGE_ID[i] = max(this_challenge_ids)
            else:
                ConfigChallengeType.AREA_START_CHALLENGE_ID[i] = 0
                ConfigChallengeType.AREA_END_CHALLENGE_ID[i] = 0

    @classmethod
    def get(cls, id):
        """

        :rtype : ChallengeMatch
        """
        return super(ConfigChallengeMatch, cls).get(id)
