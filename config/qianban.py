# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       qianban
Date Created:   2015-08-24 11:04
Description:

"""

from config.base import ConfigBase

class QianBan(object):
    __slots__ = ['id', 'condition_tp', 'condition_value', 'addition_tp', 'addition_property', 'addition_skill']
    def __init__(self):
        self.id = 0
        self.condition_tp = 0
        self.condition_value = 0
        self.addition_tp = 0
        self.addition_property = 0
        self.addition_skill = {}



class ConfigQianBan(ConfigBase):
    EntityClass = QianBan
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigQianBan, cls).initialize(fixture)
        for i in cls.INSTANCES.values():
            i.addition_skill = {int(k): v for k, v in i.addition_skill.iteritems()}

    
    @classmethod
    def get(cls, id):
        """

        :rtype : QianBan
        """
        return super(ConfigQianBan, cls).get(id)

