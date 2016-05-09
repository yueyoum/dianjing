# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       staff
Date Created:   2015-07-09 17:56
Description:

"""

import random

from config.base import ConfigBase


class RecruitResult(object):
    __slots__ = [
        'point', 'item', 'score',
    ]

    def __init__(self):
        self.point = 0
        self.item = []
        self.score = 0

class StaffRecruit(object):
    __slots__ = [
        'id', 'points', 'cost_type', 'cost_value_1', 'cost_value_10',
        'items_1', 'items_10',
        'reward_score_times', 'reward_score', 'reward_score_day_limit',
        'SPECIAL_ITEM_TP'
    ]

    def __init__(self):
        self.id = 0
        self.points = []
        self.cost_type = 0
        self.cost_value_1 = 0
        self.cost_value_10 = 0
        self.items_1 = []
        self.items_10 = []
        self.reward_score_times = 0
        self.reward_score = 0
        self.reward_score_day_limit = 0

        self.SPECIAL_ITEM_TP = 0

    def get_item(self, current_point, items=None):
        def _get():
            for point, items in self.points:
                if current_point >= point:
                    return items
            return None

        if not items:
            items = _get()
            if not items:
                return []

        prob = random.randint(1, 10000)
        for _id, _amount, _prob in items:
            if _prob >= prob:
                return [(_id, _amount)]

        return []

    def recruit(self, current_point, current_times):
        """

        :rtype: RecruitResult
        """
        from config import ConfigItemNew

        result = RecruitResult()

        # 积分
        if current_times % self.reward_score_times == 0:
            result.score = self.reward_score

        # 点数
        if current_times == 1:
            result.item = self.get_item(current_point, items=self.items_1)
        elif current_times % 10 == 0:
            result.point = 0
            result.item = self.get_item(current_point, items=self.items_10)
        else:
            result.point = 1
            result.item = self.get_item(current_point)

        if result.item:
            if ConfigItemNew.get(result.item[0][0]).tp == self.SPECIAL_ITEM_TP:
                result.point = -100

        return result


class ConfigStaffRecruit(ConfigBase):
    EntityClass = StaffRecruit

    INSTANCES = {}
    """:type: dict[int, StaffRecruit]"""
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigStaffRecruit, cls).initialize(fixture)
        for _, v in cls.INSTANCES.iteritems():
            v.points = [[int(_k), _v] for _k, _v in v.points.iteritems()]
            v.points.sort(key=lambda x: x[0], reverse=True)
            for _, items in v.points:
                for i in range(1, len(items)):
                    items[i][2] += items[i-1][2]

            for i in range(1, len(v.items_10)):
                v.items_10[i][2] += v.items_10[i-1][2]

            if v.id == 1:
                v.SPECIAL_ITEM_TP = 5
            else:
                v.SPECIAL_ITEM_TP = 6

    @classmethod
    def get(cls, _id):
        """

        :rtype: StaffRecruit
        """
        return super(ConfigStaffRecruit, cls).get(_id)


#####################################################

class StaffStep(object):
    __slots__ = [
        'attack', 'attack_percent', 'defense', 'defense_percent',
        'manage', 'manage_percent', 'operation', 'operation_percent',
        'talent_skill', 'update_item_need', 'level_limit',
    ]

    def __init__(self):
        self.attack = 0
        self.attack_percent = 0
        self.defense = 0
        self.defense_percent = 0
        self.manage = 0
        self.manage_percent = 0
        self.operation = 0
        self.operation_percent = 0
        self.talent_skill = 0
        self.update_item_need = []
        self.level_limit = 0

    @classmethod
    def create(cls, data):
        # type: (dict) -> StaffStep
        obj = cls()
        for key in cls.__slots__:
            setattr(obj, key, data[key])

        return obj


class StaffNew(object):
    __slots__ = [
        'id', 'race',
        'attack', 'attack_grow', 'defense', 'defense_grow',
        'manage', 'manage_grow', 'operation', 'operation_grow',
        'skill', 'talent_skill',
        'steps', 'max_step',
        'crystal',
    ]

    def __init__(self):
        self.id = 0
        self.race = 0
        self.attack = 0
        self.attack_grow = 0
        self.defense = 0
        self.defense_grow = 0
        self.manage = 0
        self.manage_grow = 0
        self.operation = 0
        self.operation_grow = 0
        self.skill = 0
        self.talent_skill = []
        self.steps = {}
        """:type: dict[int, StaffStep]"""
        self.max_step = 0


class StaffLevelNew(object):
    __slots__ = ['id', 'exp']

    def __init__(self):
        self.id = 0
        self.exp = 0


class StaffStar(object):
    __slots__ = [
        'id', 'exp', 'need_item_id', 'need_item_amount',
        'attack', 'attack_percent', 'defense', 'defense_percent',
        'manage', 'manage_percent', 'operation', 'operation_percent',
    ]

    def __init__(self):
        self.id = 0
        self.exp = 0
        self.need_item_id = 0
        self.need_item_amount = 0
        self.attack = 0
        self.attack_percent = 0
        self.defense = 0
        self.defense_percent = 0
        self.manage = 0
        self.manage_percent = 0
        self.operation = 0
        self.operation_percent = 0


class ConfigStaffNew(ConfigBase):
    EntityClass = StaffNew
    INSTANCES = {}
    """:type: dict[int, StaffNew]"""
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigStaffNew, cls).initialize(fixture)
        for _, obj in cls.INSTANCES.iteritems():
            steps = obj.steps
            obj.steps = {int(k): StaffStep.create(v) for k, v in steps.iteritems()}

    @classmethod
    def get(cls, _id):
        """

        :rtype: StaffNew
        """
        return super(ConfigStaffNew, cls).get(_id)


class ConfigStaffLevelNew(ConfigBase):
    EntityClass = StaffLevelNew
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        # type: (int) -> StaffLevelNew
        return super(ConfigStaffLevelNew, cls).get(_id)


class ConfigStaffStar(ConfigBase):
    EntityClass = StaffStar
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        # type: (int) -> StaffStar
        return super(ConfigStaffStar, cls).get(_id)


class StaffEquipmentQualityAddition(object):
    __slots__ = [
        'id',
        'attack', 'attack_percent',
        'defense', 'defense_percent',
        'manage', 'manage_percent',
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


class StaffEquipmentLevelAddition(object):
    __slots__ = [
        'id',
        'attack', 'attack_percent',
        'defense', 'defense_percent',
        'manage', 'manage_percent',
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


class ConfigStaffEquipmentQualityAddition(ConfigBase):
    EntityClass = StaffEquipmentQualityAddition
    INSTANCES = {}
    FILTER_CACHE = {}

    QUALITIES = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigStaffEquipmentQualityAddition, cls).initialize(fixture)
        cls.QUALITIES = cls.INSTANCES.keys()
        cls.QUALITIES.sort(reverse=True)

    @classmethod
    def get(cls, _id):
        # type: (int) -> StaffEquipmentQualityAddition
        return super(ConfigStaffEquipmentQualityAddition, cls).get(_id)

class ConfigStaffEquipmentLevelAddition(ConfigBase):
    EntityClass = StaffEquipmentLevelAddition
    INSTANCES = {}
    FILTER_CACHE = {}

    LEVELS = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigStaffEquipmentLevelAddition, cls).initialize(fixture)
        cls.LEVELS = cls.INSTANCES.keys()
        cls.LEVELS.sort(reverse=True)

    @classmethod
    def get(cls, _id):
        # type: (int) -> StaffEquipmentLevelAddition
        return super(ConfigStaffEquipmentLevelAddition, cls).get(_id)


class ConfigStaffEquipmentAddition(object):
    @classmethod
    def get_by_quality(cls, quality):
        # type: (int) -> StaffEquipmentQualityAddition | None
        for i in ConfigStaffEquipmentQualityAddition.QUALITIES:
            if quality >= i:
                return ConfigStaffEquipmentQualityAddition.get(i)

        return None

    @classmethod
    def get_by_level(cls, level):
        # type: (int) -> StaffEquipmentLevelAddition | None
        for i in ConfigStaffEquipmentLevelAddition.LEVELS:
            if level >= i:
                return ConfigStaffEquipmentLevelAddition.get(i)

        return None