# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       activity
Date Created:   2015-09-21 18:04
Description:

"""
import arrow
from config.base import ConfigBase

class ActivityCategory(object):
    __slots__ = ['id', 'mode', 'fixed', 'start_at', 'end_at']
    def __init__(self):
        self.id = 0
        self.mode = 0
        self.fixed = 0
        self.start_at = 0
        self.end_at = 0


class ConfigActivityCategory(ConfigBase):
    EntityClass = ActivityCategory
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigActivityCategory, cls).initialize(fixture)
        for i in cls.INSTANCES.values():
            if i.start_at:
                i.start_at = arrow.get(i.start_at)
                i.end_at = arrow.get(i.end_at)

    @classmethod
    def get(cls, _id):
        """

        :rtype : ActivityCategory
        """
        return super(ConfigActivityCategory, cls).get(_id)
