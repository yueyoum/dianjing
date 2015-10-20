# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training
Date Created:   2015-07-21 00:15
Description:

"""


from config.base import ConfigBase

class TrainingProperty(object):
    __slots__ = [
        'id', 'minutes', 'need_items',
        'cost_type', 'cost_value', 'package'
    ]

    def __init__(self):
        self.id = 0
        self.minutes = 0
        self.need_items = []
        self.cost_type = 0
        self.cost_value = 0
        self.package = 0


class TrainingSkillItem(object):
    __slots__ = [
        'id', 'minutes'
    ]

    def __init__(self):
        self.id = 0
        self.minutes = 0


class ConfigTrainingProperty(ConfigBase):
    EntityClass = TrainingProperty
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype : TrainingProperty
        """
        return super(ConfigTrainingProperty, cls).get(_id)


class ConfigTrainingSkillItem(ConfigBase):
    EntityClass = TrainingSkillItem
    INSTANCES = {}
    FILTER_CACHE = {}
    
    @classmethod
    def get(cls, _id):
        """

        :rtype : TrainingSkill
        """
        return super(ConfigTrainingSkillItem, cls).get(_id)
