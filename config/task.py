# -*- coding:utf-8 -*-

from config.base import ConfigBase


class Task(object):
    __slots__ = ['id', 'next_task', 'trigger',
                 'trigger_value', 'tp', 'reward',
                 'client_task', 'success_rate',
                 'task_begin', 'targets'
                 ]

    def __init__(self):
        self.id = None
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

    def is_main_task(self):
        return self.tp == 1

    def is_branch_task(self):
        return self.tp == 2

    def is_daily_task(self):
        return self.tp == 3


class RandomEvent(object):
    __slots__ = ['id', 'package']

    def __init__(self):
        self.id = 0
        self.package = 0


class TaskTargetType(object):
    __slots__ = ['id', 'mode', 'compare_type', 'compare_source', 'has_param']

    def __init__(self):
        self.id = 0
        self.mode = 0
        self.compare_type = 0
        self.compare_source = ''
        self.has_param = False


class ConfigTask(ConfigBase):
    # 类实体
    EntityClass = Task

    INSTANCES = {}
    # 过滤缓存
    FILTER_CACHE = {}

    # target and task_ids
    TARGET_TASKS = {}
    # 任务链起始任务
    HEAD_TASKS = []

    @classmethod
    def get(cls, _id):
        """

        :rtype : Task
        """
        return super(ConfigTask, cls).get(_id)

    @classmethod
    def initialize(cls, fixture):
        super(ConfigTask, cls).initialize(fixture)
        for v in cls.INSTANCES.values():
            v.targets = {(target_id, target_param): expected_value for target_id, target_param, expected_value in v.targets}

            for target_key in v.targets.keys():
                target_id, _ = target_key

                if target_id not in cls.TARGET_TASKS:
                    cls.TARGET_TASKS[target_id] = [v.id]
                else:
                    if v.id not in cls.TARGET_TASKS[target_id]:
                        cls.TARGET_TASKS[target_id].append(v.id)

            if v.task_begin:
                cls.HEAD_TASKS.append(v.id)


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


class ConfigTaskTargetType(ConfigBase):
    EntityClass = TaskTargetType
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype : TaskTargetType
        """
        return super(ConfigTaskTargetType, cls).get(_id)
