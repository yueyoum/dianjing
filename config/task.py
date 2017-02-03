# -*- coding:utf-8 -*-

import operator
from config.base import ConfigBase


class TaskCondition(object):
    __slots__ = ['id', 'server_module', 'param', 'compare_type', 'time_limit', 'CLASS', 'FUNCTION']

    def __init__(self):
        self.id = 0
        self.server_module = ''
        self.param = 0
        self.compare_type = ''
        self.time_limit = True

        self.CLASS = None
        self.FUNCTION = None

    def get_server_module(self):
        if not self.CLASS:
            cls, fn = self.server_module.split(':')

            model_name, class_name = cls.rsplit('.', 1)
            _Model = __import__(model_name, fromlist=[class_name])
            _Class = getattr(_Model, class_name)

            self.CLASS = _Class
            self.FUNCTION = fn

        return self.CLASS, self.FUNCTION

    def get_value(self, server_id, char_id, start_at=None, end_at=None):
        if self.id == 21:
            return 0

        if self.time_limit:
            if not start_at and not end_at:
                # 对于有 时间范围的 条件， 一定得有 start_at 或者 end_at
                # 都没有，就直接报错
                raise RuntimeError("TaskCondition {0} has time_limit, but call it without time limit".format(self.id))

        cls, fn = self.get_server_module()
        obj = cls(server_id, char_id)

        fn = getattr(obj, fn)

        if self.time_limit:
            if self.param:
                return fn(self.param, start_at=start_at, end_at=end_at)
            return fn(start_at=start_at, end_at=end_at)

        if self.param:
            return fn(self.param)
        return fn()

    def compare_value(self, server_id, char_id, value, target_value):
        from core.challenge import Challenge
        if self.id == 21:
            return Challenge(server_id, char_id).is_challenge_id_passed(target_value)

        if self.compare_type == '>=':
            op = operator.ge
        elif self.compare_type == '<=':
            op = operator.le
        else:
            raise RuntimeError(
                "Unknown Compare Type {0} of Condition {1}".format(
                    self.compare_type, self.id)
            )

        return op(value, target_value)


class TaskMain(object):
    __slots__ = [
        'id', 'challenge_id', 'items'
    ]

    def __init__(self):
        self.id = None
        self.challenge_id = 0
        self.items = []


class TaskDaily(object):
    __slots__ = [
        'id', 'club_level', 'vip_level', 'challenge_id',
        'condition_id', 'condition_value', 'rewards'
    ]

    def __init__(self):
        self.id = 0
        self.club_level = 0
        self.vip_level = 0
        self.challenge_id = 0
        self.condition_id = 0
        self.condition_value = 0
        self.rewards = []


class ConfigTaskCondition(ConfigBase):
    EntityClass = TaskCondition
    INSTANCES = {}
    """:type: dict[int, TaskCondition]"""
    FILTER_CACHE = {}

    SERVER_MODULE_TO_ID_TABLE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigTaskCondition, cls).initialize(fixture)
        for k, v in cls.INSTANCES.iteritems():
            if v.server_module:
                _module, _ = v.server_module.split(':')
                if _module in cls.SERVER_MODULE_TO_ID_TABLE:
                    cls.SERVER_MODULE_TO_ID_TABLE[_module].append(k)
                else:
                    cls.SERVER_MODULE_TO_ID_TABLE[_module] = [k]

    @classmethod
    def get(cls, _id):
        """

        :rtype: TaskCondition
        """
        return super(ConfigTaskCondition, cls).get(_id)

    @classmethod
    def get_condition_ids_by_name(cls, name):
        return cls.SERVER_MODULE_TO_ID_TABLE.get(name, None)


class ConfigTaskMain(ConfigBase):
    EntityClass = TaskMain
    INSTANCES = {}
    FILTER_CACHE = {}

    MAX_ID = None

    @classmethod
    def initialize(cls, fixture):
        super(ConfigTaskMain, cls).initialize(fixture)
        cls.MAX_ID = max(cls.INSTANCES.keys())

    @classmethod
    def get(cls, _id):
        """

        :rtype: TaskMain
        """
        return super(ConfigTaskMain, cls).get(_id)


class ConfigTaskDaily(ConfigBase):
    EntityClass = TaskDaily
    INSTANCES = {}
    """:type: dict[int, TaskDaily]"""
    FILTER_CACHE = {}

    CONDITION_TASK_TABLE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigTaskDaily, cls).initialize(fixture)
        for k, v in cls.INSTANCES.iteritems():
            if v.condition_id in cls.CONDITION_TASK_TABLE:
                cls.CONDITION_TASK_TABLE[v.condition_id].append(k)
            else:
                cls.CONDITION_TASK_TABLE[v.condition_id] = [k]

    @classmethod
    def get(cls, _id):
        """

        :rtype: TaskDaily
        """
        return super(ConfigTaskDaily, cls).get(_id)

    @classmethod
    def get_task_ids_by_condition_id(cls, con_id):
        return cls.CONDITION_TASK_TABLE.get(con_id, [])
