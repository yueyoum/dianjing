# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       qianban
Date Created:   2015-08-24 11:04
Description:

"""

from config.base import ConfigBase


class _QianBan(object):
    __slots__ = ['condition_tp', 'condition_value', 'talent_effect_id']

    def __init__(self):
        self.condition_tp = 0
        self.condition_value = []
        self.talent_effect_id = 0

    def __getitem__(self, item):
        return getattr(self, item)

    @classmethod
    def create(cls, data):
        obj = cls()
        obj.condition_tp = data['condition_tp']
        obj.condition_value = data['condition_value']
        obj.talent_effect_id = data['talent_effect_id']

        return obj


class _StaffQianBan(object):
    __slots__ = ['id', 'info']

    def __init__(self):
        self.id = 0
        self.info = {}
        """:type: dict[int, _QianBan]"""


class ConfigQianBan(ConfigBase):
    EntityClass = _StaffQianBan
    INSTANCES = {}
    """:type: dict[int, _StaffQianBan]"""
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigQianBan, cls).initialize(fixture)
        for _, v in cls.INSTANCES.iteritems():
            v.info = {int(_k): _QianBan.create(_v) for _k, _v in v.info.iteritems()}

    @classmethod
    def get(cls, _id):
        """

        :rtype : _StaffQianBan
        """
        return super(ConfigQianBan, cls).get(_id)


class Inspire(object):
    __slots__ = ['id', 'challenge_id']
    def __init__(self):
        self.id = 0
        self.challenge_id = 0

class ConfigInspire(ConfigBase):
    EntityClass = Inspire
    INSTANCES = {}
    FILTER_CACHE = {}

    LIST = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigInspire, cls).initialize(fixture)
        for k, v in cls.INSTANCES.iteritems():
            cls.LIST.append((v.challenge_id, k))

        cls.LIST.sort(key=lambda item: item[0])

    @classmethod
    def get_opened_ids_by_challenge_id(cls, challenge_id):
        ids = []
        for c, i in cls.LIST:
            if challenge_id < c:
                break

            ids.append(i)
        return ids

class InspireLevelAddition(object):
    __slots__ = ['id', 'attack', 'attack_percent',
                 'defense', 'defense_percent', 'manage', 'manage_percent',
                 'operation', 'operation_percent'
                 ]

    def __init__(self):
        self.id = 0
        self.attack = 0
        self.attack_percent = 0

        self.defense = 0
        self.defense_percent = 0

        self.manage = 0
        self.manage_percent = 0

        self.operation = 0
        self.operation_percent = 0


class InspireStepAddition(object):
    __slots__ = [
        'id', 'attack_percent', 'defense_percent', 'hp_percent',
        'hit_rate', 'dodge_rate', 'crit_rate', 'toughness_rate', 'crit_multiple',
        'hurt_addition_to_terran',
        'hurt_addition_to_protoss',
        'hurt_addition_to_zerg',
        'hurt_addition_by_terran',
        'hurt_addition_by_protoss',
        'hurt_addition_by_zerg',
    ]

    def __init__(self):
        self.id = 0

        self.attack_percent = 0
        self.defense_percent = 0
        self.hp_percent = 0

        self.hit_rate = 0
        self.dodge_rate = 0
        self.crit_rate = 0
        self.toughness_rate = 0
        self.crit_multiple = 0

        self.hurt_addition_to_terran = 0
        self.hurt_addition_to_protoss = 0
        self.hurt_addition_to_zerg = 0

        self.hurt_addition_by_terran = 0
        self.hurt_addition_by_protoss = 0
        self.hurt_addition_by_zerg = 0


class ConfigInspireLevelAddition(ConfigBase):
    EntityClass = InspireLevelAddition
    INSTANCES = {}
    FILTER_CACHE = {}

    LIST = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigInspireLevelAddition, cls).initialize(fixture)
        cls.LIST = cls.INSTANCES.items()
        cls.LIST.sort(key=lambda item: item[0], reverse=True)


class ConfigInspireStepAddition(ConfigBase):
    EntityClass = InspireStepAddition
    INSTANCES = {}
    FILTER_CACHE = {}

    LIST = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigInspireStepAddition, cls).initialize(fixture)
        cls.LIST = cls.INSTANCES.items()
        cls.LIST.sort(key=lambda item: item[0], reverse=True)


class ConfigInspireAddition(object):
    @classmethod
    def get_by_level(cls, level):
        """

        :rtype: InspireLevelAddition | None
        """
        for k, v in ConfigInspireLevelAddition.LIST:
            if level >= k:
                return v

        return None

    @classmethod
    def get_by_step(cls, step):
        """

        :rtype: InspireStepAddition | None
        """
        for k, v in ConfigInspireStepAddition.LIST:
            if step >= k:
                return v

        return None