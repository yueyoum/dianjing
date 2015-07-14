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
    ]




class StaffHot(object):
    __slots__ = ['id', 'cost']



class StaffRecruit(object):
    __slots__ = [
        'id', 'name', 'lucky_times', 'cost_type', 'cost_value',
        'staff_settings'
    ]

    KEY_FIRST = "first_amount"
    KEY_LUCKY = "lucky_amount"
    KEY_NORMAL = "normal_amount"


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
