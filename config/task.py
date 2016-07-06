# -*- coding:utf-8 -*-

from config.base import ConfigBase

class TaskCondition(object):
    __slots__ = ['id', 'server_module']
    def __init__(self):
        self.id = 0
        self.server_module = ''

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
        'id', 'club_level', 'vip_level', 'condition_id', 'condition_value', 'rewards'
    ]

    def __init__(self):
        self.id = 0
        self.club_level = 0
        self.vip_level = 0
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
                cls.SERVER_MODULE_TO_ID_TABLE[v.server_module] = k

    @classmethod
    def get(cls, _id):
        """

        :rtype: TaskCondition
        """
        return super(ConfigTaskCondition, cls).get(_id)

    @classmethod
    def get_condition_id_by_server_module(cls, server_module):
        return cls.SERVER_MODULE_TO_ID_TABLE.get(server_module, None)


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
