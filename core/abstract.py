# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       abstract
Date Created:   2015-07-15 14:22
Description:

"""


from protomsg.club_pb2 import Club as MessageClub
from protomsg.staff_pb2 import Staff as MessageStaff
from protomsg.unit_pb2 import Unit as MessageUnit

from config import ConfigStaffStar


class AbstractUnit(object):
    __slots__ = [
        'conf_unit',
        'id', 'step', 'level',

        'hp', 'hp_percent', 'attack', 'attack_percent', 'defense', 'defense_percent',
        'attack_speed', 'attack_speed_percent',
        'attack_range', 'attack_range_percent',
        'move_speed', 'move_speed_percent',
        'hit_rate', 'dodge_rate', 'crit_rate', 'toughness_rate', 'crit_multi',

        'hurt_addition_to_terran', 'hurt_addition_to_protoss', 'hurt_addition_to_zerg',
        'hurt_addition_by_terran', 'hurt_addition_by_protoss', 'hurt_addition_by_zerg',

        'final_hurt_addition', 'final_hurt_reduce',
    ]

    def __init__(self):
        self.conf_unit = None
        """:type: config.unit.Unit"""

        self.id = 0  # NOTE: 就是本身的ID
        self.step = 0
        self.level = 0

        self.hp = 0
        self.hp_percent = 0.0
        self.attack = 0
        self.attack_percent = 0.0
        self.defense = 0
        self.defense_percent = 0.0
        self.attack_speed = 0
        self.attack_speed_percent = 0.0
        self.attack_range = 0
        self.attack_range_percent = 0.0
        self.move_speed = 0
        self.move_speed_percent = 0.0
        self.hit_rate = 0.0
        self.dodge_rate = 0.0
        self.crit_rate = 0.0
        self.toughness_rate = 0.0
        self.crit_multi = 0.0

        self.hurt_addition_to_terran = 0.0
        self.hurt_addition_to_protoss = 0.0
        self.hurt_addition_to_zerg = 0.0
        self.hurt_addition_by_terran = 0.0
        self.hurt_addition_by_protoss = 0.0
        self.hurt_addition_by_zerg = 0.0

        self.final_hurt_addition = 0
        self.final_hurt_reduce = 0

    def pre_calculate_property(self):
        conf_step = self.conf_unit.steps[self.step]

        self.hp_percent = conf_step.hp_percent
        self.attack_percent = conf_step.attack_percent
        self.defense_percent = conf_step.defense_percent

        self.attack_speed = self.conf_unit.attack_speed_base
        self.attack_range = self.conf_unit.attack_range_base
        self.move_speed = self.conf_unit.move_speed_base
        self.hit_rate = self.conf_unit.hit_rate + conf_step.hit_rate
        self.dodge_rate = self.conf_unit.dodge_rate + conf_step.dodge_rate
        self.crit_rate = self.conf_unit.crit_rate + conf_step.crit_rate
        self.crit_multi = self.conf_unit.crit_multiple + conf_step.crit_multiple
        self.toughness_rate = self.conf_unit.toughness_rate + conf_step.toughness_rate
        self.hurt_addition_to_terran = self.conf_unit.hurt_addition_to_terran + conf_step.hurt_addition_to_terran
        self.hurt_addition_to_protoss = self.conf_unit.hurt_addition_to_protoss + conf_step.hurt_addition_to_protoss
        self.hurt_addition_to_zerg = self.conf_unit.hurt_addition_to_zerg + conf_step.hurt_addition_to_zerg
        self.hurt_addition_by_terran = self.conf_unit.hurt_addition_by_terran + conf_step.hurt_addition_by_terran
        self.hurt_addition_by_protoss = self.conf_unit.hurt_addition_by_protoss + conf_step.hurt_addition_by_protoss
        self.hurt_addition_by_zerg = self.conf_unit.hurt_addition_by_zerg + conf_step.hurt_addition_by_zerg
        self.final_hurt_addition = self.conf_unit.final_hurt_addition
        self.final_hurt_reduce = self.conf_unit.final_hurt_reduce

    def calculate_property(self):
        conf_level = self.conf_unit.levels[self.level]
        self.hp = int((self.conf_unit.hp_max_base + conf_level.hp) * (1 + self.hp_percent))
        self.attack = int((self.conf_unit.attack_base + conf_level.attack) * (1 + self.attack_percent))
        self.defense = int((self.conf_unit.defense_base + conf_level.defense) * (1 + self.defense_percent))

    def make_protomsg(self):
        # type: () -> MessageUnit
        msg = MessageUnit()
        msg.id = self.id
        msg.level = self.level
        msg.step = self.step
        msg.hp = self.hp
        msg.attack = self.attack
        msg.defense = self.defense
        return msg


class AbstractStaff(object):
    __slots__ = [
        'config',
        'server_id', 'char_id', 'id', 'oid', 'level', 'step', 'star', 'level_exp', 'star_exp',
        'active_qianban_ids',

        'equip_mouse', 'equip_keyboard', 'equip_monitor', 'equip_decoration',
        'attack', 'defense', 'manage', 'operation',
        'attack_percent', 'defense_percent', 'manage_percent', 'operation_percent',

        'quality',

        'formation_position',
        'unit'
    ]

    def __init__(self, *args, **kwargs):
        self.config = None
        """:type: config.staff.Staff"""

        self.server_id = 0
        self.char_id = 0

        self.id = ''
        self.oid = 0
        self.level = 1
        self.step = 1
        self.star = 0
        self.level_exp = 0
        self.star_exp = 0
        self.active_qianban_ids = []

        self.equip_mouse = ''
        self.equip_keyboard = ''
        self.equip_monitor = ''
        self.equip_decoration = ''
        self.attack = 0
        self.defense = 0
        self.manage = 0
        self.operation = 0
        self.attack_percent = 0
        self.defense_percent = 0
        self.manage_percent = 0
        self.operation_percent = 0

        self.quality = 0

        self.formation_position = -1
        self.unit = None
        """:type: AbstractUnit"""

    def calculate_property(self):
        self.attack = self.config.attack + (self.level - 1) * self.config.attack_grow
        self.defense = self.config.defense + (self.level - 1) * self.config.defense_grow
        self.manage = self.config.manage + (self.level - 1) * self.config.manage_grow
        self.operation = self.config.operation + (self.level - 1) * self.config.operation_grow

        step_config = self.config.steps[self.step]
        self.attack += step_config.attack
        self.defense += step_config.defense
        self.manage += step_config.manage
        self.operation += step_config.operation
        self.attack_percent += step_config.attack_percent
        self.defense_percent += step_config.defense_percent
        self.manage_percent += step_config.manage_percent
        self.operation_percent += step_config.operation_percent

        star_config = ConfigStaffStar.get(self.star)
        self.attack += star_config.attack
        self.defense += star_config.defense
        self.manage += star_config.manage
        self.operation += star_config.operation
        self.attack_percent += star_config.attack_percent
        self.defense_percent += star_config.defense_percent
        self.manage_percent += star_config.manage_percent
        self.operation_percent += star_config.operation_percent

        # TODO 装备加成， 天赋加成

    @property
    def power(self):
        # TODO
        return 0

    def is_initial_state(self):
        # type: () -> bool
        if self.level != 1:
            return False

        if self.step != 0:
            return False

        if self.star != (self.quality - 1) * 10:
            return False

        if self.level_exp > 0 or self.star_exp > 0:
            return False

        return True

    def make_protomsg(self):
        msg = MessageStaff()
        msg.id = self.id
        msg.oid = self.oid
        msg.level = self.level
        msg.step = self.step
        msg.star = self.star
        msg.level_exp = self.level_exp
        msg.star_exp = self.star_exp
        msg.attack = self.attack
        msg.defense = self.defense
        msg.manage = self.manage
        msg.operation = self.operation
        msg.equip_mouse_slot_id = self.equip_mouse
        msg.equip_keyboard_slot_id = self.equip_keyboard
        msg.equip_monitor_slot_id = self.equip_monitor
        msg.equip_decoration_slot_id = self.equip_decoration

        return msg


class AbstractClub(object):
    __slots__ = [
        'id', 'name', 'manager_name', 'flag', 'level',
        'renown', 'vip', 'gold', 'diamond', 'crystal', 'gas',
        'formation_staffs',
    ]

    def __init__(self, *args, **kwargs):
        self.id = 0
        self.name = ""
        self.manager_name = ""
        self.flag = 0
        self.level = 1
        self.renown = 0
        self.vip = 0
        self.gold = 0
        self.diamond = 0
        self.crystal = 0
        self.gas = 0
        self.formation_staffs = []
        """:type: list[AbstractStaff]"""

    def qianban_affect(self):
        pass

    def get_power(self):
        # TODO
        return 999

    def make_protomsg(self):
        msg = MessageClub()
        # 因为NPC的ID是UUID，所以这里为了统一，club的ID 都是 str
        msg.id = str(self.id)
        msg.name = self.name
        msg.manager = self.manager_name
        msg.flag = self.flag
        msg.level = self.level
        msg.renown = self.renown
        msg.vip = self.vip
        msg.gold = self.gold
        msg.diamond = self.diamond
        msg.crystal = self.crystal
        msg.gas = self.gas

        return msg
