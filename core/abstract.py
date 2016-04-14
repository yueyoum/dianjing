# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       abstract
Date Created:   2015-07-15 14:22
Description:

"""

from utils import cache

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

    def calculate(self):
        # 等级
        config_level = self.config.levels[self.level]
        self.hp = self.config.hp_max_base + config_level.hp
        self.attack = self.config.attack_base + config_level.attack
        self.defense = self.config.defense_base + config_level.defense

        # 阶
        config_step = self.config.steps[self.step]
        self.hp_percent += config_step.hp_percent
        self.attack_percent += config_step.attack_percent
        self.defense_percent += config_step.defense_percent
        self.attack_speed += self.config.attack_speed_base
        self.attack_range += self.config.attack_range_base
        self.move_speed += self.config.move_speed_base
        self.hit_rate += self.config.hit_rate + config_step.hit_rate
        self.dodge_rate += self.config.dodge_rate + config_step.dodge_rate
        self.crit_rate += self.config.crit_rate + config_step.crit_rate
        self.crit_multi += self.config.crit_multiple + config_step.crit_multiple
        self.toughness_rate += self.config.toughness_rate + config_step.toughness_rate
        self.hurt_addition_to_terran += self.config.hurt_addition_to_terran + config_step.hurt_addition_to_terran
        self.hurt_addition_to_protoss += self.config.hurt_addition_to_protoss + config_step.hurt_addition_to_protoss
        self.hurt_addition_to_zerg += self.config.hurt_addition_to_zerg + config_step.hurt_addition_to_zerg
        self.hurt_addition_by_terran += self.config.hurt_addition_by_terran + config_step.hurt_addition_by_terran
        self.hurt_addition_by_protoss += self.config.hurt_addition_by_protoss + config_step.hurt_addition_by_protoss
        self.hurt_addition_by_zerg += self.config.hurt_addition_by_zerg + config_step.hurt_addition_by_zerg
        self.final_hurt_addition += self.config.final_hurt_addition
        self.final_hurt_reduce += self.config.final_hurt_reduce

        # 最终属性
        self.hp = int(self.hp * (1 + self.hp_percent))
        self.attack = int(self.attack * (1 + self.attack_percent))
        self.defense = int(self.defense * (1 + self.defense_percent))

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
        # 不同的staff可以带同一个兵种，
        # 兵种在外面显示的属性 只是兵种自己的，
        # 但进入战斗后，就需要对这些unit做一个clone操作，
        # 这样不同staff带的unit就有不一样的表现
        '__unit',

        'active_talent_ids',
    ]

    def __init__(self):
        self.config = None
        """:type: config.staff.StaffNew"""

        self.server_id = None
        self.char_id = None

        self.id = ''
        self.oid = 0
        self.level = 1
        self.step = 0
        self.star = 0
        self.level_exp = 0
        self.star_exp = 0

        self.attack = 0
        self.defense = 0
        self.manage = 0
        self.operation = 0
        self.attack_percent = 0
        self.defense_percent = 0
        self.manage_percent = 0
        self.operation_percent = 0

        self.quality = 0
        self.equip_mouse = ''
        self.equip_keyboard = ''
        self.equip_monitor = ''
        self.equip_decoration = ''
        self.active_qianban_ids = []

        self.formation_position = None

        self.__unit = None
        """:type: AbstractUnit"""

        self.active_talent_ids = []

    @classmethod
    def get(cls, _id):
        # type: (str) -> AbstractStaff | None
        key = 'staff:{0}'.format(_id)
        return cache.get(key)

    def make_cache(self):
        key = 'staff:{0}'.format(self.id)
        cache.set(key, self)

    def after_init(self):
        self.config = ConfigStaffNew.get(self.oid)
        self.quality = ConfigItemNew.get(self.oid).quality

    @property
    def unit(self):
        return self.__unit

    def calculate(self):
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

        # 天赋
        for tid in self.active_talent_ids:
            config_talent = ConfigTalentSkill.get(tid)
            if config_talent.target <= 5:
                # 对选手的
                self._add_talent_effect_to_staff(config_talent)
            else:
                # 对兵的
                if self.__unit:
                    if config_talent.target in [6, 10]:
                        self._add_talent_effect_to_unit(config_talent)
                    elif config_talent.target in [7, 11] and self.__unit.config.race == 1:
                        self._add_talent_effect_to_unit(config_talent)
                    elif config_talent.target in [8, 12] and self.__unit.config.race == 3:
                        self._add_talent_effect_to_unit(config_talent)
                    elif config_talent.target in [9, 13] and self.__unit.config.race == 2:
                        self._add_talent_effect_to_unit(config_talent)

        # 最终属性
        self.attack = int(self.attack * (1 + self.attack_percent))
        self.defense = int(self.attack * (1 + self.defense_percent))
        self.manage = int(self.attack * (1 + self.manage_percent))
        self.operation = int(self.attack * (1 + self.operation_percent))

    def set_unit(self, unit):
        # type: (AbstractUnit) -> None
        self.__unit = unit.clone()

    def get_all_equipment_quality(self):
        return 0

    def get_all_equipment_level(self):
        return 0

    def get_self_talent_skill_ids(self):
        ids = []
        ids.extend(self.config.talent_skill)
        for i in range(0, self.step + 1):
            if self.config.steps[i].talent_skill:
                ids.append(self.config.steps[i].talent_skill)

        return ids

    def talent_effect(self, club):
        """

        :param club:
        :type club: AbstractClub
        """
        # 天赋影响
        for tid in self.get_self_talent_skill_ids():
            config_talent = ConfigTalentSkill.get(tid)
            if config_talent.target == 1:
                # 选手自身
                self.active_talent_ids.append(tid)
            elif config_talent.target == 2:
                # 上阵所有选手
                for s in club.formation_staffs:
                    s.active_talent_ids.append(tid)
            elif config_talent.target == 3:
                # 上阵所有人族选手
                for s in club.get_formation_terran_staffs():
                    s.active_talent_ids.append(tid)
            elif config_talent.target == 4:
                # 上阵所有虫族选手
                for s in club.get_formation_zerg_staffs():
                    s.active_talent_ids.append(tid)
            elif config_talent.target == 5:
                # 上阵所有神族选手
                for s in club.get_formation_protoss_staffs():
                    s.active_talent_ids.append(tid)

            # 因为选手的带的兵也会随时变化，所以这里就直接把和兵相关的 天赋 记录下来
            # 这样就不用更换了兵种后再来判断天赋影响
            elif config_talent.target == 6:
                # 选手自身携带的任意兵种
                self.active_talent_ids.append(tid)
            elif config_talent.target == 7:
                # 选手自身携带的人族兵种
                self.active_talent_ids.append(tid)
            elif config_talent.target == 8:
                # 选手自身携带的虫族并种
                self.active_talent_ids.append(tid)
            elif config_talent.target == 9:
                # 选手自身携带的神族并种
                self.active_talent_ids.append(tid)

            elif config_talent.target == 10:
                # 所有选手所有任意兵种
                for s in club.formation_staffs:
                    s.active_talent_ids.append(tid)
            elif config_talent.target == 11:
                # 所有选手所有人族兵种
                for s in club.formation_staffs:
                    s.active_talent_ids.append(tid)
            elif config_talent.target == 12:
                # 所有选手所有虫族兵种
                for s in club.formation_staffs:
                    s.active_talent_ids.append(tid)
            elif config_talent.target == 13:
                # 所有选手所有神族兵种
                for s in club.formation_staffs:
                    s.active_talent_ids.append(tid)

    def _add_talent_effect_to_staff(self, config):
        """

        :param config:
        :type config: config.skill.TalentSkill
        :return:
        """
        self.attack += config.staff_attack
        self.attack_percent += config.staff_attack_percent
        self.defense += config.staff_defense
        self.defense_percent += config.staff_defense_percent
        self.manage += config.staff_manage
        self.manage_percent += config.staff_manage_percent
        self.operation += config.staff_operation
        self.operation_percent += config.staff_operation_percent

    def _add_talent_effect_to_unit(self, config):
        """

        :param config:
        :type config: config.skill.TalentSkill
        :return:
        """
        self.__unit.hp_percent += config.unit_hp_percent
        self.__unit.attack_percent += config.unit_attack_percent
        self.__unit.defense_percent += config.unit_defense_percent
        self.__unit.hit_rate += config.unit_hit_rate
        self.__unit.dodge_rate += config.unit_dodge_rate
        self.__unit.crit_rate += config.unit_crit_rate
        self.__unit.toughness_rate += config.unit_toughness_rate
        self.__unit.crit_multi += config.unit_crit_multiple
        self.__unit.hurt_addition_to_terran += config.unit_hurt_addition_to_terran
        self.__unit.hurt_addition_to_protoss += config.unit_hurt_addition_to_protoss
        self.__unit.hurt_addition_to_zerg += config.unit_hurt_addition_to_zerg

        self.__unit.hurt_addition_by_terran += config.unit_hurt_addition_by_terran
        self.__unit.hurt_addition_by_protoss += config.unit_hurt_addition_by_protoss
        self.__unit.hurt_addition_by_zerg += config.unit_hurt_addition_by_zerg

        self.__unit.final_hurt_addition += config.unit_final_hurt_addition
        self.__unit.final_hurt_reduce += config.unit_final_hurt_reduce

        self.__unit.calculate()

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

    def load_staffs(self):
        raise NotImplementedError()

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
