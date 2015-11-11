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
        'jingong', 'jingong_grow',
        'qianzhi', 'qianzhi_grow',
        'xintai', 'xintai_grow',
        'baobing', 'baobing_grow',
        'fangshou', 'fangshou_grow',
        'yunying', 'yunying_grow',
        'yishi', 'yishi_grow',
        'caozuo', 'caozuo_grow',
        'skill_ids',
        'qianban_ids',
    ]

    def __init__(self):
        self.id = None
        self.name = None
        self.nation = None
        self.race = None
        self.quality = None
        self.buy_type = None
        self.buy_cost = None
        self.can_recruit = None

        self.jingong = None
        self.jingong_grow = None
        self.qianzhi = None
        self.qianzhi_grow = None
        self.xintai = None
        self.xintai_grow = None
        self.baobing = None
        self.baobing_grow = None
        self.fangshou = None
        self.fangshou_grow = None
        self.yunying = None
        self.yunying_grow = None
        self.yishi = None
        self.yishi_grow = None
        self.caozuo = None
        self.caozuo_grow = None

        self.skill_ids = None
        self.qianban_ids = None



class StaffHot(object):
    __slots__ = ['id', 'cost']

    def __init__(self):
        self.id = 0
        self.cost = 0



class StaffRecruit(object):
    __slots__ = [
        'id', 'name', 'lucky_times', 'cost_type', 'cost_value',
        'staff_settings'
    ]

    KEY_FIRST = "first_amount"
    KEY_LUCKY = "lucky_amount"
    KEY_NORMAL = "normal_amount"

    def __init__(self):
        self.id = None
        self.name = None
        self.lucky_times = None
        self.cost_type = None
        self.cost_value = None
        self.staff_settings = None


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
    def get(cls, id):
        """

        :param id: staff id
        :type id: int
        :return: Staff object
        :rtype: Staff
        """
        return super(ConfigStaff, cls).get(id)


    @classmethod
    def get_random_ids_by_condition(cls, amount, **condition):
        """

        :rtype : list
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
    def get(cls, id):
        """

        :param id: staff hot id
        :type  id: int
        :return: StaffHot object
        :rtype : StaffHot
        """
        return super(ConfigStaffHot, cls).get(id)


    @classmethod
    def random_three(cls):
        """

        :rtype : list
        """
        ids = cls.INSTANCES.keys()
        return random.sample(ids, 3)


class ConfigStaffRecruit(ConfigBase):
    EntityClass = StaffRecruit

    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, id):
        """

        :rtype: StaffRecruit
        """
        return super(ConfigStaffRecruit, cls).get(id)


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
            if i+1 == length:
                instances[i][1].next_level = None
            else:
                instances[i][1].next_level = instances[i+1][0]


    @classmethod
    def get(cls, id):
        """

        :rtype : StaffLevel
        """
        return super(ConfigStaffLevel, cls).get(id)

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
