# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       activity_login_reward
Date Created:   2015-09-22 10:45
Description:

"""

from config.base import ConfigBase

class LoginReward(object):
    __slots__ = ['id', 'category', 'day', 'package']
    def __init__(self):
        self.id = 0
        self.category = 0
        self.day = 0
        self.package = 0


class ConfigLoginReward(ConfigBase):
    EntityClass = LoginReward
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype : LoginReward
        """
        return super(ConfigLoginReward, cls).get(_id)
