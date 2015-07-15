# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       unit
Date Created:   2015-07-15 16:01
Description:

"""


from config.base import ConfigBase

class Unit(object):
    __slots__ = [
        'id', 'race',
        'first_trig', 'second_trig', 'third_trig',
        'des'
    ]

    def __init__(self):
        self.id = None
        self.race = None
        self.first_trig = None
        self.second_trig = None
        self.third_trig = None
        self.des = None


class ConfigUnit(ConfigBase):
    EntityClass = Unit
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, id):
        """

        :rtype : Unit
        """
        return super(ConfigUnit, cls).get(id)

