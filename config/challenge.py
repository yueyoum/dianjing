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
        'id', 'level'
    ]


class ChallengeMatch(object):
    __slots__ = [
        'id', 'need_club_level', 'tp', 'policy', 'level', 'strength', 'staffs', 'package',
        'club_name', 'club_flag'
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


class ConfigChallengeType(ConfigBase):
    EntityClass = ChallengeType
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, id):
        """

        :rtype : ChallengeType
        """
        return super(ConfigChallengeType, cls).get(id)


class ConfigChallengeMatch(ConfigBase):
    EntityClass = ChallengeMatch
    INSTANCES = {}
    FILTER_CACHE = {}

    FIRST_ID = 1
    LAST_ID = None

    @classmethod
    def initialize(cls, fixture):
        super(ConfigChallengeMatch, cls).initialize(fixture)
        cls.LAST_ID = max(cls.INSTANCES.keys())

    @classmethod
    def get(cls, id):
        """

        :rtype : ChallengeMatch
        """
        return super(ConfigChallengeMatch, cls).get(id)
