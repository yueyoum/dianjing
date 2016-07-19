# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       formation
Date Created:   2016-06-22 17-53
Description:

"""

from config.base import ConfigBase

class Slot(object):
    __slots__ = ['id', 'club_level']
    def __init__(self):
        self.id = 0
        self.club_level = 0


class ConfigFormationSlot(ConfigBase):
    EntityClass = Slot
    INSTANCES = {}
    """:type: dict[int, Slot]"""
    FILTER_CACHE = {}

    @classmethod
    def get_opened_slot_ids(cls, club_level):
        ids = []
        for k, v in cls.INSTANCES.iteritems():
            if club_level >= v.club_level:
                ids.append(k)

        ids.sort()
        return ids


class FormationLevel(object):
    __slots__ = ['level_up_need_star', 'talent_effects']
    def __init__(self):
        self.level_up_need_star = 0
        self.talent_effects = []

    @classmethod
    def create(cls, data):
        """

        :rtype: FormationLevel
        """
        obj = cls()
        obj.level_up_need_star = data['level_up_need_star']
        obj.talent_effects = data['talent_effects']


class Formation(object):
    __slots__ = [
        'active_need_star',
        'active_need_items',
        'use_condition',
        'levels',
        'max_level'
    ]

    def __init__(self):
        self.active_need_star = 0
        self.active_need_items = []
        self.use_condition = []
        self.max_level = 0
        self.levels = {}
        """:type: dict[int, FormationLevel]"""


class ConfigFormation(ConfigBase):
    EntityClass = Formation
    INSTANCES = {}
    """:type: dict[int, Formation]"""
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigFormation, cls).initialize(fixture)
        for k, v in cls.INSTANCES.iteritems():
            v.levels = {int(_k): FormationLevel.create(_v) for _k, _v in v.levels.iteritems()}

    @classmethod
    def get(cls, _id):
        """

        :rtype: Formation
        """
        return super(ConfigFormation, cls).get(_id)