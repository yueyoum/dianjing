# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       staff
Date Created:   2015-07-09 17:56
Description:

"""

import random

from config.base import ConfigBase


class StaffHot(object):
    __slots__ = ['id', 'cost']

    def __init__(self):
        self.id = 0
        self.cost = 0


class StaffRecruit(object):
    __slots__ = [
        'id', 'lucky_times', 'cost_type', 'cost_value',
        'staff_settings'
    ]

    KEY_FIRST = "first_amount"
    KEY_LUCKY = "lucky_amount"
    KEY_NORMAL = "normal_amount"

    def __init__(self):
        self.id = 0
        self.lucky_times = 0
        self.cost_type = 0
        self.cost_value = 0
        self.staff_settings = {}

    def get_refreshed_staffs(self, first=False, lucky=False):
        """

        :rtype : list
        """
        if first:
            key = self.KEY_FIRST
        elif lucky:
            key = self.KEY_LUCKY
        else:
            key = self.KEY_NORMAL

        staffs = []
        for s in self.staff_settings:
            value = s[key]
            if not value:
                continue

            staffs.append((s['quality'], value))

        return staffs


class ConfigStaffHot(ConfigBase):
    EntityClass = StaffHot

    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype : StaffHot
        """
        return super(ConfigStaffHot, cls).get(_id)

    @classmethod
    def random_three(cls):
        """

        :rtype : list[int]
        """
        ids = cls.INSTANCES.keys()
        return random.sample(ids, 3)


class ConfigStaffRecruit(ConfigBase):
    EntityClass = StaffRecruit

    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: StaffRecruit
        """
        return super(ConfigStaffRecruit, cls).get(_id)


#####################################################

class StaffStep(object):
    __slots__ = [
        'attack', 'attack_percent', 'defense', 'defense_percent',
        'manage', 'manage_percent', 'operation', 'operation_percent',
        'talent_skill', 'update_item_need', 'level_limit',
    ]

    def __init__(self):
        self.attack = 0
        self.attack_percent = 0
        self.defense = 0
        self.defense_percent = 0
        self.manage = 0
        self.manage_percent = 0
        self.operation = 0
        self.operation_percent = 0
        self.talent_skill = 0
        self.update_item_need = []
        self.level_limit = 0

    @classmethod
    def create(cls, data):
        # type: (dict) -> StaffStep
        obj = cls()
        for key in cls.__slots__:
            setattr(obj, key, data[key])

        return obj


class StaffNew(object):
    __slots__ = [
        'id', 'race',
        'attack', 'attack_grow', 'defense', 'defense_grow',
        'manage', 'manage_grow', 'operation', 'operation_grow',
        'skill', 'talent_skill',
        'steps', 'max_step',
        'crystal',
    ]

    def __init__(self):
        self.id = 0
        self.race = 0
        self.attack = 0
        self.attack_grow = 0
        self.defense = 0
        self.defense_grow = 0
        self.manage = 0
        self.manage_grow = 0
        self.operation = 0
        self.operation_grow = 0
        self.skill = 0
        self.talent_skill = []
        self.steps = {}
        """:type: dict[int, StaffStep]"""
        self.max_step = 0


class StaffLevelNew(object):
    __slots__ = ['id', 'exp']

    def __init__(self):
        self.id = 0
        self.exp = 0


class StaffStar(object):
    __slots__ = [
        'id', 'exp', 'need_item_id', 'need_item_amount',
        'attack', 'attack_percent', 'defense', 'defense_percent',
        'manage', 'manage_percent', 'operation', 'operation_percent',
    ]

    def __init__(self):
        self.id = 0
        self.exp = 0
        self.need_item_id = 0
        self.need_item_amount = 0
        self.attack = 0
        self.attack_percent = 0
        self.defense = 0
        self.defense_percent = 0
        self.manage = 0
        self.manage_percent = 0
        self.operation = 0
        self.operation_percent = 0


class ConfigStaffNew(ConfigBase):
    EntityClass = StaffNew
    INSTANCES = {}
    """:type: dict[int, StaffNew]"""
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigStaffNew, cls).initialize(fixture)
        for _, obj in cls.INSTANCES.iteritems():
            steps = obj.steps
            obj.steps = {int(k): StaffStep.create(v) for k, v in steps.iteritems()}

    @classmethod
    def get(cls, _id):
        """

        :rtype: StaffNew
        """
        return super(ConfigStaffNew, cls).get(_id)


class ConfigStaffLevelNew(ConfigBase):
    EntityClass = StaffLevelNew
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        # type: (int) -> StaffLevelNew
        return super(ConfigStaffLevelNew, cls).get(_id)


class ConfigStaffStar(ConfigBase):
    EntityClass = StaffStar
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        # type: (int) -> StaffStar
        return super(ConfigStaffStar, cls).get(_id)
