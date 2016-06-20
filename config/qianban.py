# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       qianban
Date Created:   2015-08-24 11:04
Description:

"""

from config.base import ConfigBase


class _QianBan(object):
    __slots__ = ['condition_tp', 'condition_value', 'talent_effect_id']

    def __init__(self):
        self.condition_tp = 0
        self.condition_value = []
        self.talent_effect_id = 0

    def __getitem__(self, item):
        return getattr(self, item)

    @classmethod
    def create(cls, data):
        obj = cls()
        obj.condition_tp = data['condition_tp']
        obj.condition_value = data['condition_value']
        obj.talent_effect_id = data['talent_effect_id']

        return obj


class _StaffQianBan(object):
    __slots__ = ['id', 'info']

    def __init__(self):
        self.id = 0
        self.info = {}
        """:type: dict[int, _QianBan]"""


class ConfigQianBan(ConfigBase):
    EntityClass = _StaffQianBan
    INSTANCES = {}
    """:type: dict[int, _StaffQianBan]"""
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigQianBan, cls).initialize(fixture)
        for _, v in cls.INSTANCES.iteritems():
            v.info = {int(_k): _QianBan.create(_v) for _k, _v in v.info.iteritems()}

    @classmethod
    def get(cls, _id):
        """

        :rtype : _StaffQianBan
        """
        return super(ConfigQianBan, cls).get(_id)
