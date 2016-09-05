# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       name
Date Created:   2016-09-05 16:20
Description:

"""

import random
from config.base import ConfigBase

class Name(object):
    __slots__ = ['id', 'name']
    def __init__(self):
        self.id = 0
        self.name = ''


class ConfigFirstName(ConfigBase):
    EntityClass = Name
    INSTANCES = {}
    FILTER_CACHE = {}

    NAMES = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigFirstName, cls).initialize(fixture)
        cls.NAMES = [v.name for _, v in cls.INSTANCES.iteritems()]

class ConfigLastName(ConfigBase):
    EntityClass = Name
    INSTANCES = {}
    FILTER_CACHE = {}

    NAMES = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigLastName, cls).initialize(fixture)
        cls.NAMES = [v.name for _, v in cls.INSTANCES.iteritems()]


class ConfigName(object):
    @classmethod
    def get_random_name(cls):
        a = random.choice(ConfigLastName.NAMES)
        b = random.choice(ConfigFirstName.NAMES)

        return "{0}．{1}".format(a, b)
