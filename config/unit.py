# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       unit
Date Created:   2015-07-15 16:01
Description:

"""


from config.base import ConfigBase

class UnitLevel(object):
    __slots__ = [
        'hp', 'attack', 'defense', 'update_item_need'
    ]

    def __init__(self):
        self.hp = 0
        self.attack = 0
        self.defense = 0
        self.update_item_need = []


    @classmethod
    def create(cls, data):
        # type: (dict) -> UnitLevel
        obj = cls()
        for k in cls.__slots__:
            setattr(obj, k, data[k])

        return obj


class UnitStep(object):
    __slots__ = [
        'level_limit', 'update_item_need', 'hp_percent', 'attack_percent', 'defense_percent',
        'hit_rate', 'dodge_rate', 'crit_rate', 'toughness_rate', 'crit_multiple',
        'hurt_addition_to_terran', 'hurt_addition_to_protoss', 'hurt_addition_to_zerg',
        'hurt_addition_by_terran', 'hurt_addition_by_protoss', 'hurt_addition_by_zerg',
    ]

    def __init__(self):
        self.level_limit = 0
        self.update_item_need = 0
        self.hp_percent = 0
        self.attack_percent = 0
        self.defense_percent = 0
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


    @classmethod
    def create(cls, data):
        # type: (dict) -> UnitStep
        obj = cls()
        for k in cls.__slots__:
            setattr(obj, k, data[k])

        return obj


class UnitNew(object):
    __slots__ = [
        'id', 'tp', 'race', 'attack_tp', 'defense_tp', 'operation',
        'skill_1', 'skill_2',
        'hp_max_base', 'attack_base', 'defense_base',
        'attack_speed_base', 'attack_range_base', 'move_speed_base',
        'hit_rate', 'dodge_rate', 'crit_rate', 'toughness_rate',
        'crit_multiple',
        'hurt_addition_to_terran',
        'hurt_addition_to_protoss',
        'hurt_addition_to_zerg',
        'hurt_addition_by_terran',
        'hurt_addition_by_protoss',
        'hurt_addition_by_zerg',
        'final_hurt_addition',
        'final_hurt_reduce',

        'levels',
        'max_level',
        'steps',
        'max_step',
    ]

    def __init__(self):
        self.id = 0
        self.tp = 0
        self.race = 0
        self.attack_tp = 0
        self.defense_tp = 0
        self.operation = 0
        self.skill_1 = 0
        self.skill_2 = 0
        self.hp_max_base = 0
        self.attack_base = 0
        self.defense_base = 0
        self.attack_speed_base = 0
        self.attack_range_base = 0
        self.move_speed_base = 0
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
        self.final_hurt_addition = 0
        self.final_hurt_reduce = 0

        self.levels = {}
        """:type: dict[int, UnitLevel]"""
        self.max_level = 0
        self.steps = {}
        """:type: dict[int, UnitStep]"""
        self.max_step = 0


class ConfigUnitNew(ConfigBase):
    EntityClass = UnitNew
    INSTANCES = {}
    """:type: dict[int, UnitNew]"""
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigUnitNew, cls).initialize(fixture)
        for _, obj in cls.INSTANCES.iteritems():
            obj.levels = {int(k): UnitLevel.create(v) for k, v in obj.levels.iteritems()}
            obj.steps = {int(k): UnitStep.create(v) for k, v in obj.steps.iteritems()}

    @classmethod
    def get(cls, _id):
        """

        :rtype: UnitNew
        """
        return super(ConfigUnitNew, cls).get(_id)


class UnitUnLock(object):
    __slots__ = [
        'id', 'need_club_level', 'need_unit_level'
    ]

    def __init__(self):
        self.id = 0
        self.need_club_level = 0
        self.need_unit_level = []


class ConfigUnitUnLock(ConfigBase):
    EntityClass = UnitUnLock
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        # type: (int) -> UnitUnLock
        return super(ConfigUnitUnLock, cls).get(_id)


class _LevelAddition(object):
    __slots__ = [
        'level',
        'hp_percent', 'attack_percent', 'defense_percent',
        'hit_rate', 'dodge_rate', 'crit_rate', 'toughness_rate', 'crit_multiple',
        'hurt_addition_to_terran', 'hurt_addition_to_protoss', 'hurt_addition_to_zerg',
        'hurt_addition_by_terran', 'hurt_addition_by_protoss', 'hurt_addition_by_zerg',
    ]

    @classmethod
    def create(cls, data):
        # type: (dict) -> _LevelAddition
        obj = cls()
        for attr in cls.__slots__:
            setattr(obj, attr, data[attr])

        return obj

class _StepAddition(object):
    __slots__ = [
        'step',
        'hp_percent', 'attack_percent', 'defense_percent',
        'hit_rate', 'dodge_rate', 'crit_rate', 'toughness_rate', 'crit_multiple',
        'hurt_addition_to_terran', 'hurt_addition_to_protoss', 'hurt_addition_to_zerg',
        'hurt_addition_by_terran', 'hurt_addition_by_protoss', 'hurt_addition_by_zerg',
    ]

    @classmethod
    def create(cls, data):
        # type: (dict) -> _StepAddition
        obj = cls()
        for attr in cls.__slots__:
            setattr(obj, attr, data[attr])

        return obj


class UnitLevelAddition(object):
    __slots__ = ['id', 'addition']

    def __init__(self):
        self.id = 0
        self.addition = []
        """:type: list[_LevelAddition]"""

class UnitStepAddition(object):
    __slots__ = ['id', 'addition']

    def __init__(self):
        self.id = 0
        self.addition = []
        """:type: list[_StepAddition]"""


class ConfigUnitLevelAddition(ConfigBase):
    EntityClass = UnitLevelAddition
    INSTANCES = {}
    """:type: dict[int, UnitLevelAddition]"""
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigUnitLevelAddition, cls).initialize(fixture)
        for _, v in cls.INSTANCES.iteritems():
            v.addition = [_LevelAddition.create(x) for x in v.addition]
            v.addition.sort(key=lambda item: item.level, reverse=True)


class ConfigUnitStepAddition(ConfigBase):
    EntityClass = UnitStepAddition
    INSTANCES = {}
    """:type: dict[int, UnitStepAddition]"""
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigUnitStepAddition, cls).initialize(fixture)
        for _, v in cls.INSTANCES.iteritems():
            v.addition = [_StepAddition.create(x) for x in v.addition]
            v.addition.sort(key=lambda item: item.step, reverse=True)


class ConfigUnitAddition(object):
    @classmethod
    def get_level_addition(cls, race, level):
        # type: (int, int) -> _LevelAddition|None
        for a in ConfigUnitLevelAddition.INSTANCES[race].addition:
            if level >= a.level:
                return a

        return None

    @classmethod
    def get_step_addition(cls, race, step):
        # type: (int, int) -> _StepAddition|None
        for a in ConfigUnitStepAddition.INSTANCES[race].addition:
            if step >= a.step:
                return a

        return None