__author__ = 'hikaly'
# -*- coding:utf-8 -*-
from config.base import ConfigBase
import random

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

