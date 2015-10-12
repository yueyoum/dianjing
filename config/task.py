# -*- coding:utf-8 -*-

from config.base import ConfigBase

class Task(object):
    __slots__ = ['id', 'name', 'level',
                 'tp', 'num', 'reward',
                 'client_task', 'success_rate'
                 ]

    def __init__(self):
        self.id = None
        self.name = None
        self.level = None
        self.tp = None
        self.num = None
        self.reward = None
        self.client_task = False
        self.success_rate = 0

    @property
    def package(self):
        return self.reward


class RandomEvent(object):
    __slots__ = ['id', 'package']
    def __init__(self):
        self.id = 0
        self.package = 0

class ConfigTask(ConfigBase):
    # 类实体
    EntityClass = Task

    INSTANCES = {}
    # 过滤缓存
    FILTER_CACHE = {}

    @classmethod
    def get(cls, id):
        """

        :rtype : Task
        """
        return super(ConfigTask, cls).get(id)


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
