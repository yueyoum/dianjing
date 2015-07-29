__author__ = 'hikaly'
# -*- coding:utf-8 -*-
from config.base import ConfigBase
import random

class Task(object):
    __slots__ = ['id', 'name', 'level', 'des',
                 'tp', 'num', 'package']

    def __init__(self):
        self.id = None
        self.name = None
        self.level = None
        self.des = None
        self.tp = None
        self.num = None
        self.package = None

class ConfigTask(ConfigBase):
    # 类实体
    EntityClass = Task

    INSTANCES = {}
    # 过滤缓存
    FILTER_CACHE = {}

    @classmethod
    def get(cls, id):
        """

        :rtype : Unit
        """
        return super(ConfigTask, cls).get(id)

    @classmethod
    def check(cls, id):
        """

        :param id:
        :return:
        """
        return super(ConfigTask, cls).check(id)

