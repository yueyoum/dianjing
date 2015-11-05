# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       club
Date Created:   2015-07-28 15:38
Description:

"""

from config.base import ConfigBase


class ClubLevel(object):
    __slots__ = ['id', 'renown', 'next_level_id', 'max_staff_amount']

    def __init__(self):
        self.id = 0
        self.renown = 0
        self.next_level_id = 0
        self.max_staff_amount = 0


class ClubFlag(object):
    __slots__ = ['id', 'flag']

    def __init__(self):
        self.id = 0
        self.flag = 0


class ConfigClubLevel(ConfigBase):
    EntityClass = ClubLevel
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigClubLevel, cls).initialize(fixture)

        instances = cls.INSTANCES.items()
        instances.sort(key=lambda item: item[0])

        length = len(instances)
        for i in range(length):
            if i + 1 == length:
                instances[i][1].next_level_id = None
            else:
                instances[i][1].next_level_id = instances[i + 1][0]

    @classmethod
    def get(cls, id):
        """

        :rtype : ClubLevel
        """
        return super(ConfigClubLevel, cls).get(id)


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
