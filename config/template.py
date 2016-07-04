# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       template
Date Created:   2016-07-04 17-22
Description:

"""

from config.base import ConfigBase

class Broadcast(object):
    __slots__ = ['id', 'template']
    def __init__(self):
        self.id = 0
        self.template = ''


class ConfigBroadcastTemplate(ConfigBase):
    EntityClass = Broadcast
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: Broadcast
        """
        return super(ConfigBroadcastTemplate, cls).get(_id)
    