# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       staff
Date Created:   2015-07-09 17:56
Description:

"""

import json

class Staff(object):
    __slot__ = [
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


class ConfigStaff(object):
    STAFFS = {}
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        for f in fixture:
            s = Staff()
            s.id = f['pk']
            for k, v in f['fields'].iteritems():
                if k not in Staff.__slot__:
                    continue

                setattr(s, k, v)

            cls.STAFFS[s.id] = s

    @classmethod
    def get(cls, id):
        """

        :param id: staff id
        :type id: int
        :return: staff config object
        :rtype: Staff
        """
        return cls.STAFFS[id]

    @classmethod
    def filter(cls, **condition):
        """

        :rtype : dict
        """
        cache_key = json.dumps(condition)
        if cache_key not in cls.FILTER_CACHE:
            result = {}

            for k, v in cls.STAFFS.iteritems():
                if cls._do_filter(v, **condition):
                    result[k] = v

            cls.FILTER_CACHE[cache_key] = result

        return cls.FILTER_CACHE[cache_key]

    @classmethod
    def _do_filter(cls, obj, **condition):
        for k, v in condition.iteritems():
            if getattr(obj, k) != v:
                return False
            return True
