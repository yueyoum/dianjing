# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       signin
Date Created:   2015-09-21 14:58
Description:

"""

from config.base import ConfigBase

class SignIn(object):
    __slots__ = ['id', 'circle_times', 'circle_package',
                 'valid_test_divisor', 'valid_test_value',
                 'day_reward',
                 'mail_title', 'mail_content',

                 'days',
                 'max_day',
                 ]

    def __init__(self):
        self.id = 0
        self.circle_times = 0
        self.circle_package = 0
        self.valid_test_divisor = 0
        self.valid_test_value = 0
        self.day_reward = 0
        self.mail_title = 0
        self.mail_content = 0
        self.days = []
        self.max_day = 0


class ConfigSignIn(ConfigBase):
    EntityClass = SignIn
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigSignIn, cls).initialize(fixture)

        for i in cls.INSTANCES.values():
            i.day_reward = {int(k): v for k, v in i.day_reward.iteritems()}
            i.days = i.day_reward.keys()
            i.days.sort()
            i.max_day = max(i.days)
    
    @classmethod
    def get(cls, _id):
        """

        :rtype : SignIn
        """
        return super(ConfigSignIn, cls).get(_id)
