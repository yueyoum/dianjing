# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       staff
Date Created:   2015-07-09 17:56
Description:

"""

import random

from config.base import ConfigBase


class Staff(object):
    __slots__ = [
        'id', 'name', 'nation', 'race', 'quality', 'buy_type', 'buy_cost',
        'can_recruit',
        'skill_ids',
        'qianban_ids',

        'luoji',
        'minjie',
        'lilun',
        'wuxing',
        'meili',
    ]

    def __init__(self):
        self.id = 0
        self.name = ""
        self.nation = 0
        self.race = 0
        self.quality = 0
        self.buy_type = 0
        self.buy_cost = 0
        self.can_recruit = False

        self.skill_ids = 0
        self.qianban_ids = 0

        self.luoji = 0
        self.minjie = 0
        self.lilun = 0
        self.wuxing = 0
        self.meili = 0


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


class StaffLevel(object):
    __slots__ = ['id', 'exp', 'next_level']

    def __init__(self):
        self.id = 0
        self.exp = {}
        self.next_level = 0


class StaffStatus(object):
    __slots__ = ['id', 'value']

    def __init__(self):
        self.id = 0
        self.value = 0


class ConfigStaff(ConfigBase):
    EntityClass = Staff

    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: Staff
        """
        return super(ConfigStaff, cls).get(_id)

    @classmethod
    def get_random_ids_by_condition(cls, amount, **condition):
        """

        :rtype : list[int]
        """
        data = cls.filter(**condition)
        return random.sample(data.keys(), amount)

    @classmethod
    def random_ids(cls, amount):
        return random.sample(cls.INSTANCES.keys(), amount)


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


class ConfigStaffLevel(ConfigBase):
    EntityClass = StaffLevel

    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigStaffLevel, cls).initialize(fixture)

        instances = cls.INSTANCES.items()
        instances.sort(key=lambda item: item[0])

        length = len(instances)
        for i in range(length):
            if i + 1 == length:
                instances[i][1].next_level = None
            else:
                instances[i][1].next_level = instances[i + 1][0]

    @classmethod
    def get(cls, _id):
        """

        :rtype : StaffLevel
        """
        return super(ConfigStaffLevel, cls).get(_id)


class ConfigStaffStatus(ConfigBase):
    EntityClass = StaffStatus
    INSTANCES = {}
    FILTER_CACHE = {}

    DEFAULT_STATUS = 0

    @classmethod
    def initialize(cls, fixture):
        super(ConfigStaffStatus, cls).initialize(fixture)

        for k, v in cls.INSTANCES.iteritems():
            if v.value == 0:
                cls.DEFAULT_STATUS = k
                break
        else:
            raise Exception("can not find default staff status")

    @classmethod
    def get(cls, _id):
        """

        :rtype : StaffStatus
        """
        return super(ConfigStaffStatus, cls).get(_id)
