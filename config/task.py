# -*- coding:utf-8 -*-

from config.base import ConfigBase


class Task(object):
    __slots__ = ['id', 'name', 'des', 'next_task', 'trigger',
                 'trigger_value', 'tp', 'reward',
                 'client_task', 'success_rate',
                 'task_begin', 'targets'
                 ]

    def __init__(self):
        self.id = None
        self.name = None
        self.des = None
        self.next_task = None
        self.trigger = None
        self.trigger_value = 0
        self.tp = None
        self.reward = None
        self.client_task = False
        self.success_rate = 0
        self.task_begin = 0
        self.targets = {}

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

    @classmethod
    def initialize(cls, fixture):
        super(ConfigTask, cls).initialize(fixture)
        for v in cls.INSTANCES.values():
            v.targets = {a: b for a, b in v.targets}


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
