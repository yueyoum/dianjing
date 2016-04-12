# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       skill
Date Created:   2015-07-24 11:21
Description:

"""

from config.base import ConfigBase


class TalentSkill(object):
    __slots__ = [
        'id', 'target',
        'staff_attack', 'staff_attack_percent',
        'staff_defense', 'staff_defense_percent',
        'staff_manage', 'staff_manage_percent',
        'staff_operation', 'staff_operation_percent',

        'unit_hp_percent', 'unit_attack_percent', 'unit_defense_percent',
        'unit_hit_rate', 'unit_dodge_rate', 'unit_crit_rate',
        'unit_toughness_rate', 'unit_crit_multiple',

        'unit_hurt_addition_to_terran',
        'unit_hurt_addition_to_protoss',
        'unit_hurt_addition_to_zerg',

        'unit_hurt_addition_by_terran',
        'unit_hurt_addition_by_protoss',
        'unit_hurt_addition_by_zerg',

        'unit_final_hurt_addition',
        'unit_final_hurt_reduce',
    ]

    def __init__(self):
        self.id = 0
        self.target = 0
        self.staff_attack = 0
        self.staff_attack_percent = 0
        self.staff_defense = 0
        self.staff_defense_percent = 0
        self.staff_manage = 0
        self.staff_manage_percent = 0
        self.staff_operation = 0
        self.staff_operation_percent = 0

        self.unit_hp_percent = 0
        self.unit_attack_percent = 0
        self.unit_defense_percent = 0
        self.unit_hit_rate = 0
        self.unit_dodge_rate = 0
        self.unit_crit_rate = 0
        self.unit_toughness_rate = 0
        self.unit_crit_multiple = 0

        self.unit_hurt_addition_to_terran = 0
        self.unit_hurt_addition_to_protoss = 0
        self.unit_hurt_addition_to_zerg = 0

        self.unit_hurt_addition_by_terran = 0
        self.unit_hurt_addition_by_protoss = 0
        self.unit_hurt_addition_by_zerg = 0

        self.unit_final_hurt_addition = 0
        self.unit_final_hurt_reduce = 0


class ConfigTalentSkill(ConfigBase):
    EntityClass = TalentSkill
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        # type: (int) -> TalentSkill
        return super(ConfigTalentSkill, cls).get(_id)