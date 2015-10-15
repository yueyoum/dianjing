# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       signin
Date Created:   2015-09-21 14:58
Description:

"""

from config.base import ConfigBase

class SignIn(object):
    __slots__ = ['id', 'circle_package',
                 'day_reward',
                 'mail_title', 'mail_content',
                 'days'
                 ]

    def __init__(self):
        self.id = 0
        self.circle_package = 0
        self.day_reward = {}
        self.mail_title = ''
        self.mail_content = ''
        self.days = []

    def get_package_id(self, day):
        return self.day_reward[day]


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

    @classmethod
    def get(cls, _id):
        """

        :rtype : SignIn
        """
        return super(ConfigSignIn, cls).get(_id)
