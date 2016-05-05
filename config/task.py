# -*- coding:utf-8 -*-

from config.base import ConfigBase


class TaskMain(object):
    __slots__ = [
        'id', 'challenge_id', 'items'
    ]

    def __init__(self):
        self.id = None
        self.challenge_id = 0
        self.items = []


class RandomEvent(object):
    __slots__ = ['id', 'package']

    def __init__(self):
        self.id = 0
        self.package = 0


class ConfigRandomEvent(ConfigBase):
    EntityClass = RandomEvent
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype : RandomEvent
        """
        return super(ConfigRandomEvent, cls).get(_id)


class ConfigTaskMain(ConfigBase):
    EntityClass = TaskMain
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: TaskMain
        """
        return super(ConfigTaskMain, cls).get(_id)