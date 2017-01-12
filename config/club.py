# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       club
Date Created:   2015-07-28 15:38
Description:

"""
import random
from config.base import ConfigBase


class ClubLevel(object):
    __slots__ = ['id', 'exp', 'energy']

    def __init__(self):
        self.id = 0
        self.exp = 0
        self.energy = 0

class ClubFlag(object):
    __slots__ = ['id', 'flag']

    def __init__(self):
        self.id = 0
        self.flag = ''


class ConfigClubLevel(ConfigBase):
    EntityClass = ClubLevel
    INSTANCES = {}
    FILTER_CACHE = {}

    MAX_LEVEL = None

    @classmethod
    def initialize(cls, fixture):
        super(ConfigClubLevel, cls).initialize(fixture)
        cls.MAX_LEVEL = max(cls.INSTANCES.keys())

    @classmethod
    def get(cls, _id):
        """

        :rtype : ClubLevel
        """
        return super(ConfigClubLevel, cls).get(_id)


class ConfigClubFlag(ConfigBase):
    EntityClass = ClubFlag
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype : ClubFlag
        """
        return super(ConfigClubFlag, cls).get(_id)

    @classmethod
    def get_random_flag_id(cls):
        return random.choice(cls.INSTANCES.keys())
