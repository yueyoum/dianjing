# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       abstract
Date Created:   2015-07-15 14:22
Description:

"""

import weakref

from protomsg.club_pb2 import Club as MessageClub
from protomsg.staff_pb2 import Staff as MessageStaff
from protomsg.unit_pb2 import Unit as MessageUnit

from config import ConfigStaffStar, ConfigStaffNew, ConfigUnitNew, ConfigItemNew, ConfigStaffEquipmentAddition, \
    ConfigTalentSkill


class AbstractUnit(object):
    __slots__ = [
        'config',
        'server_id', 'char_id',
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
        self.config = None
        """:type: config.unit.UnitNew"""

        self.server_id = None
        self.char_id = None

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

    def after_init(self):
        self.config = ConfigUnitNew.get(self.id)
        self.pre_calculate()
        self.calculate()

    def pre_calculate(self):
        config_step = self.config.steps[self.step]

        self.hp_percent = config_step.hp_percent
        self.attack_percent = config_step.attack_percent
        self.defense_percent = config_step.defense_percent

        self.attack_speed = self.config.attack_speed_base
        self.attack_range = self.config.attack_range_base
        self.move_speed = self.config.move_speed_base
        self.hit_rate = self.config.hit_rate + config_step.hit_rate
        self.dodge_rate = self.config.dodge_rate + config_step.dodge_rate
        self.crit_rate = self.config.crit_rate + config_step.crit_rate
        self.crit_multi = self.config.crit_multiple + config_step.crit_multiple
        self.toughness_rate = self.config.toughness_rate + config_step.toughness_rate
        self.hurt_addition_to_terran = self.config.hurt_addition_to_terran + config_step.hurt_addition_to_terran
        self.hurt_addition_to_protoss = self.config.hurt_addition_to_protoss + config_step.hurt_addition_to_protoss
        self.hurt_addition_to_zerg = self.config.hurt_addition_to_zerg + config_step.hurt_addition_to_zerg
        self.hurt_addition_by_terran = self.config.hurt_addition_by_terran + config_step.hurt_addition_by_terran
        self.hurt_addition_by_protoss = self.config.hurt_addition_by_protoss + config_step.hurt_addition_by_protoss
        self.hurt_addition_by_zerg = self.config.hurt_addition_by_zerg + config_step.hurt_addition_by_zerg
        self.final_hurt_addition = self.config.final_hurt_addition
        self.final_hurt_reduce = self.config.final_hurt_reduce

    def calculate(self):
        config_level = self.config.levels[self.level]
        self.hp = int((self.config.hp_max_base + config_level.hp) * (1 + self.hp_percent))
        self.attack = int((self.config.attack_base + config_level.attack) * (1 + self.attack_percent))
        self.defense = int((self.config.defense_base + config_level.defense) * (1 + self.defense_percent))

    def clone(self):
        # type: () -> AbstractUnit
        obj = AbstractUnit()
        for attr in self.__class__.__slots__:
            setattr(obj, attr, getattr(self, attr))

        return obj

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
        '__unit',

        'talent_skills',

        'club_weakref',
    ]

    def __init__(self):
        self.config = None
        """:type: config.staff.StaffNew"""

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

        self.formation_position = None
        self.__unit = None
        """:type: AbstractUnit"""

        self.talent_skills = []
        """:type: list[int]"""

        self.club_weakref = None
        """:type: AbstractClub"""

    def after_init(self):
        self.config = ConfigStaffNew.get(self.oid)
        self.quality = ConfigItemNew.get(self.oid).quality

        self.talent_skills.extend(self.config.talent_skill)
        for i in range(0, self.step + 1):
            if self.config.steps[i].talent_skill:
                self.talent_skills.append(self.config.steps[i].talent_skill)

        self.pre_calculate()

    def pre_calculate(self):
        # 等级
        self.attack = self.config.attack + (self.level - 1) * self.config.attack_grow
        self.defense = self.config.defense + (self.level - 1) * self.config.defense_grow
        self.manage = self.config.manage + (self.level - 1) * self.config.manage_grow
        self.operation = self.config.operation + (self.level - 1) * self.config.operation_grow

        # 阶
        step_config = self.config.steps[self.step]
        self.attack += step_config.attack
        self.defense += step_config.defense
        self.manage += step_config.manage
        self.operation += step_config.operation
        self.attack_percent += step_config.attack_percent
        self.defense_percent += step_config.defense_percent
        self.manage_percent += step_config.manage_percent
        self.operation_percent += step_config.operation_percent

        # 星
        star_config = ConfigStaffStar.get(self.star)
        self.attack += star_config.attack
        self.defense += star_config.defense
        self.manage += star_config.manage
        self.operation += star_config.operation
        self.attack_percent += star_config.attack_percent
        self.defense_percent += star_config.defense_percent
        self.manage_percent += star_config.manage_percent
        self.operation_percent += star_config.operation_percent

        # 装备
        equip_level_addition = ConfigStaffEquipmentAddition.get_by_level(self.get_all_equipment_level())
        if equip_level_addition:
            self.attack += equip_level_addition.attack
            self.attack_percent += equip_level_addition.attack_percent
            self.defense += equip_level_addition.defense
            self.defense_percent += equip_level_addition.defense_percent
            self.manage += equip_level_addition.manage
            self.manage_percent += equip_level_addition.manage_percent

        equip_quality_addition = ConfigStaffEquipmentAddition.get_by_quality(self.get_all_equipment_quality())
        if equip_quality_addition:
            self.attack += equip_quality_addition.attack
            self.attack_percent += equip_quality_addition.attack_percent
            self.defense += equip_quality_addition.defense
            self.defense_percent += equip_quality_addition.defense_percent
            self.manage += equip_quality_addition.manage
            self.manage_percent += equip_quality_addition.manage_percent

    def calculate(self):
        # 最终属性， 处理完天赋的
        self.attack *= 1 + self.attack_percent
        self.defense *= 1 + self.defense_percent
        self.manage *= 1 + self.manage_percent
        self.operation *= 1 + self.operation_percent

    def set_unit(self, unit):
        # type: (AbstractUnit) -> None
        self.__unit = unit.clone()

    def get_all_equipment_quality(self):
        return 0

    def get_all_equipment_level(self):
        return 0

    def talent_effect(self):
        # 天赋影响
        for tid in self.talent_skills:
            config_talent = ConfigTalentSkill.get(tid)
            if config_talent.target == 1:
                # 选手自身
                self._add_talent_effect_to_staff(config_talent, [self])
            elif config_talent.target == 2:
                # 上阵所有选手
                self._add_talent_effect_to_staff(config_talent, self.club_weakref.formation_staffs)
            elif config_talent.target == 3:
                # 上阵所有人族选手
                self._add_talent_effect_to_staff(config_talent, self.club_weakref.get_formation_terran_staffs())
            elif config_talent.target == 4:
                # 上阵所有虫族选手
                self._add_talent_effect_to_staff(config_talent, self.club_weakref.get_formation_zerg_staffs())
            elif config_talent.target == 5:
                # 上阵所有神族选手
                self._add_talent_effect_to_staff(config_talent, self.club_weakref.get_formation_protoss_staffs())
            elif config_talent.target == 6:
                # 选手自身携带的任意兵种
                self._add_talent_effect_to_unit(config_talent, [self.__unit])
            elif config_talent.target == 7:
                # 选手自身携带的人族兵种
                if self.__unit.config.race == 1:
                    self._add_talent_effect_to_unit(config_talent, [self.__unit])
            elif config_talent.target == 8:
                # 选手自身携带的虫族并种
                if self.__unit.config.race == 3:
                    self._add_talent_effect_to_unit(config_talent, [self.__unit])
            elif config_talent.target == 9:
                # 选手自身携带的神族并种
                if self.__unit.config.race == 2:
                    self._add_talent_effect_to_unit(config_talent, [self.__unit])
            elif config_talent.target == 10:
                # 所有选手所有任意兵种
                self._add_talent_effect_to_unit(config_talent, self.club_weakref.get_formation_all_units())
            elif config_talent.target == 11:
                # 所有选手所有人族兵种
                self._add_talent_effect_to_unit(config_talent, self.club_weakref.get_formation_terran_units())
            elif config_talent.target == 12:
                # 所有选手所有虫族兵种
                self._add_talent_effect_to_unit(config_talent, self.club_weakref.get_formation_zerg_units())
            elif config_talent.target == 13:
                # 所有选手所有神族兵种
                self._add_talent_effect_to_unit(config_talent, self.club_weakref.get_formation_protoss_units())

    def _add_talent_effect_to_staff(self, config, staff_list):
        """

        :param config:
        :param staff_list:
        :type config: config.skill.TalentSkill
        :type staff_list: list[AbstractStaff]
        :return:
        """

        for s in staff_list:
            s.attack += config.staff_attack
            s.attack_percent += config.staff_attack_percent
            s.defense += config.staff_defense
            s.defense_percent += config.staff_defense_percent
            s.manage += config.staff_manage
            s.manage_percent += config.staff_manage_percent
            s.operation += config.staff_operation
            s.operation_percent += config.staff_operation_percent
            s.calculate()

    def _add_talent_effect_to_unit(self, config, unit_list):
        """

        :param config:
        :param unit_list:
        :type config: config.skill.TalentSkill
        :type unit_list: list[AbstractUnit]
        :return:
        """
        for u in unit_list:
            u.hp_percent += config.unit_hp_percent
            u.attack_percent += config.unit_attack_percent
            u.defense_percent += config.unit_defense_percent
            u.hit_rate += config.unit_hit_rate
            u.dodge_rate += config.unit_dodge_rate
            u.crit_rate += config.unit_crit_rate
            u.toughness_rate += config.unit_toughness_rate
            u.crit_multi += config.unit_crit_multiple
            u.hurt_addition_to_terran += config.unit_hurt_addition_to_terran
            u.hurt_addition_to_protoss += config.unit_hurt_addition_to_protoss
            u.hurt_addition_to_zerg += config.unit_hurt_addition_to_zerg

            u.hurt_addition_by_terran += config.unit_hurt_addition_by_terran
            u.hurt_addition_by_protoss += config.unit_hurt_addition_by_protoss
            u.hurt_addition_by_zerg += config.unit_hurt_addition_by_zerg

            u.final_hurt_addition += config.unit_final_hurt_addition
            u.final_hurt_reduce += config.unit_final_hurt_reduce

            u.calculate()

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
        msg.attack = int(self.attack)
        msg.defense = int(self.defense)
        msg.manage = int(self.manage)
        msg.operation = self.operation
        msg.equip_mouse_slot_id = self.equip_mouse
        msg.equip_keyboard_slot_id = self.equip_keyboard
        msg.equip_monitor_slot_id = self.equip_monitor
        msg.equip_decoration_slot_id = self.equip_decoration

        return msg


class AbstractClub(object):
    __slots__ = [
        'server_id', 'char_id',
        'id', 'name', 'manager_name', 'flag', 'level',
        'renown', 'vip', 'gold', 'diamond', 'crystal', 'gas',
        'formation_staffs',
    ]

    def __init__(self):
        self.server_id = None
        self.char_id = None

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

    def load_formation_staffs(self):
        # 设置 self.formation_staffs
        raise NotImplementedError()

    def after_load_formation_staffs(self):
        ref = weakref.proxy(self)
        for s in self.formation_staffs:
            s.club_weakref = ref

    def get_formation_terran_staffs(self):
        return [s for s in self.formation_staffs if s.config.race == 1]

    def get_formation_protoss_staffs(self):
        return [s for s in self.formation_staffs if s.config.race == 2]

    def get_formation_zerg_staffs(self):
        return [s for s in self.formation_staffs if s.config.race == 3]

    def get_formation_all_units(self):
        # type: () -> list[AbstractUnit]
        units = []
        for s in self.formation_staffs:
            if s.__unit:
                units.append(s.__unit)

        return units

    def get_formation_terran_units(self):
        # type: () -> list[AbstractUnit]
        units = []
        for s in self.formation_staffs:
            if s.__unit and s.__unit.config.race == 1:
                units.append(s.__unit)

        return units

    def get_formation_protoss_units(self):
        # type: () -> list[AbstractUnit]
        units = []
        for s in self.formation_staffs:
            if s.__unit and s.__unit.config.race == 2:
                units.append(s.__unit)

        return units

    def get_formation_zerg_units(self):
        # type: () -> list[AbstractUnit]
        units = []
        for s in self.formation_staffs:
            if s.__unit and s.__unit.config.race == 3:
                units.append(s.__unit)

        return units

    def talent_effect(self):
        for s in self.formation_staffs:
            s.talent_effect()

    def qianban_affect(self):
        pass

    @property
    def power(self):
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
