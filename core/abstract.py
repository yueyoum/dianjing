# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       abstract
Date Created:   2015-07-15 14:22
Description:

"""
import math
from utils import cache

from protomsg.club_pb2 import Club as MessageClub
from protomsg.staff_pb2 import Staff as MessageStaff
from protomsg.unit_pb2 import Unit as MessageUnit

from config import (
    ConfigStaffStar,
    ConfigStaffNew,
    ConfigUnitNew,
    ConfigItemNew,
    ConfigTalentSkill,
    ConfigQianBan,
)


class DummyConfig(object):
    def __getattr__(self, _):
        return 0


class AbstractUnit(object):
    __slots__ = [
        'config',
        'server_id', 'char_id',
        'id', 'step', 'level',

        'hp', 'hp_percent', 'attack', 'attack_percent', 'defense', 'defense_percent',

        'attack_speed', 'attack_speed_percent',
        'attack_range', 'attack_range_percent',
        'move_speed', 'move_speed_percent',
        'hit_rate', 'dodge_rate', 'crit_rate', 'toughness_rate', 'crit_multiple',

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
        self.crit_multiple = 0.0

        self.hurt_addition_to_terran = 0.0
        self.hurt_addition_to_protoss = 0.0
        self.hurt_addition_to_zerg = 0.0
        self.hurt_addition_by_terran = 0.0
        self.hurt_addition_by_protoss = 0.0
        self.hurt_addition_by_zerg = 0.0

        self.final_hurt_addition = 0
        self.final_hurt_reduce = 0

    @classmethod
    def get(cls, char_id, _id):
        # type: (str) -> AbstractUnit | None
        key = 'unit:{0}:{1}'.format(char_id, _id)
        return cache.get(key)

    def make_cache(self):
        key = 'unit:{0}:{1}'.format(self.char_id, self.id)
        cache.set(key, self)

    def after_init(self):
        self.config = ConfigUnitNew.get(self.id)

    def calculate(self):
        # 阶
        if self.config.max_step:
            config_step = self.config.steps[self.step]
        else:
            config_step = DummyConfig()

        self.hp_percent = config_step.hp_percent
        self.attack_percent = config_step.attack_percent
        self.defense_percent = config_step.defense_percent
        self.attack_speed = self.config.attack_speed_base
        self.attack_range = self.config.attack_range_base
        self.move_speed = self.config.move_speed_base
        self.hit_rate = self.config.hit_rate + config_step.hit_rate
        self.dodge_rate = self.config.dodge_rate + config_step.dodge_rate
        self.crit_rate = self.config.crit_rate + config_step.crit_rate
        self.crit_multiple = self.config.crit_multiple + config_step.crit_multiple
        self.toughness_rate = self.config.toughness_rate + config_step.toughness_rate
        self.hurt_addition_to_terran = self.config.hurt_addition_to_terran + config_step.hurt_addition_to_terran
        self.hurt_addition_to_protoss = self.config.hurt_addition_to_protoss + config_step.hurt_addition_to_protoss
        self.hurt_addition_to_zerg = self.config.hurt_addition_to_zerg + config_step.hurt_addition_to_zerg
        self.hurt_addition_by_terran = self.config.hurt_addition_by_terran + config_step.hurt_addition_by_terran
        self.hurt_addition_by_protoss = self.config.hurt_addition_by_protoss + config_step.hurt_addition_by_protoss
        self.hurt_addition_by_zerg = self.config.hurt_addition_by_zerg + config_step.hurt_addition_by_zerg
        self.final_hurt_addition = self.config.final_hurt_addition
        self.final_hurt_reduce = self.config.final_hurt_reduce

        # 对于在外部展示unit属性的， 这里直接调用calculate就行了.
        # 要进入战斗的unit，会有各种buff加成，
        # 这时候就把各种加成先加上， 然后再调用一次 final_calculate
        self.final_calculate()

    def final_calculate(self):
        # 最终属性
        if self.config.max_level:
            config_level = self.config.levels[self.level]
        else:
            config_level = DummyConfig()

        hp = self.config.hp_max_base + config_level.hp
        attack = self.config.attack_base + config_level.attack
        defense = self.config.defense_base + config_level.defense

        # self.hp = int(hp * (1 + self.hp_percent))
        # self.attack = int(attack * (1 + self.attack_percent))
        # self.defense = int(defense * (1 + self.defense_percent))
        self.hp = int(hp)
        self.attack = int(attack)
        self.defense = int(defense)

    def clone(self):
        # type: () -> AbstractUnit
        obj = AbstractUnit()
        for attr in AbstractUnit.__slots__:
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

        'equip_mouse', 'equip_keyboard', 'equip_monitor', 'equip_decoration',
        'attack', 'defense', 'manage', 'operation',
        'attack_percent', 'defense_percent', 'manage_percent', 'operation_percent',

        'formation_position',
        # 不同的staff可以带同一个兵种，
        # 兵种在外面显示的属性 只是兵种自己的，
        # 但进入战斗后，就需要对这些unit做一个clone操作，
        # 这样不同staff带的unit就有不一样的表现
        '__unit',

        # 自身的天赋
        'self_talent_ids',
        # 外部加的天赋，比如 天赋树，图鉴，等等
        'other_talent_ids',
        # 激活的牵绊
        'active_qianban_ids',
        # 牵绊的天赋
        'qianban_talent_ids',
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

        self.equip_mouse = ''
        self.equip_keyboard = ''
        self.equip_monitor = ''
        self.equip_decoration = ''

        self.formation_position = None

        self.__unit = None
        """:type: AbstractUnit"""

        self.self_talent_ids = []
        self.other_talent_ids = []
        self.active_qianban_ids = []
        self.qianban_talent_ids = []

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

    def check_activie_qianban_ids(self):
        config = ConfigQianBan.get(self.oid)
        if not config:
            return

        qianban_ids = []
        talent_effect_ids = []
        for k, v in config.info.iteritems():
            # TODO  more condition_tp
            if v.condition_tp == 1:
                # 装备兵种
                if self.__unit and self.__unit.id in v.condition_value:
                    qianban_ids.append(k)
                    talent_effect_ids.append(v.talent_effect_id)

        self.active_qianban_ids = qianban_ids
        self.qianban_talent_ids = talent_effect_ids

    @property
    def unit(self):
        return self.__unit

    def get_active_talent_ids(self):
        # 牵绊的天赋效果可能会频繁变动，比如兵种变化
        return self.self_talent_ids + self.other_talent_ids + self.qianban_talent_ids

    def calculate(self):
        # 等级
        self.attack = self.config.attack + (self.level - 1) * self.config.attack_grow
        self.defense = self.config.defense + (self.level - 1) * self.config.defense_grow
        self.manage = self.config.manage + (self.level - 1) * self.config.manage_grow
        self.operation = self.config.operation + (self.level - 1) * self.config.operation_grow

        # 阶
        if self.config.max_step:
            step_config = self.config.steps[self.step]
        else:
            step_config = DummyConfig()

        self.attack += step_config.attack
        self.defense += step_config.defense
        self.manage += step_config.manage
        self.operation += step_config.operation

        self.attack_percent = step_config.attack_percent
        self.defense_percent = step_config.defense_percent
        self.manage_percent = step_config.manage_percent
        self.operation_percent = step_config.operation_percent

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
        self.add_equipment_property()

        # 天赋
        for tid in self.get_active_talent_ids():
            config_talent = ConfigTalentSkill.get(tid)
            if config_talent.target <= 5:
                # 对选手的
                self._add_talent_effect_to_staff(config_talent)

        # 最终属性
        self.attack = int(self.attack * (1 + self.attack_percent))
        self.defense = int(self.defense * (1 + self.defense_percent))
        self.manage = int(self.manage * (1 + self.manage_percent))
        self.operation = int(self.operation * (1 + self.operation_percent))

        self.calculate_unit()

    def set_unit(self, unit):
        # type: (AbstractUnit) -> None
        self.__unit = unit.clone()
        self.check_activie_qianban_ids()

    def calculate_unit(self):
        if not self.server_id:
            return

        from core.unit import UnitManager
        if not self.__unit:
            return

        unit = UnitManager(self.server_id, self.char_id).get_unit_object(self.__unit.id)
        self.__unit = unit.clone()

        for tid in self.get_active_talent_ids():
            config_talent = ConfigTalentSkill.get(tid)
            if config_talent.target <= 5:
                continue

            if config_talent.target in [6, 10] or \
                    (config_talent.target in [7, 11] and self.__unit.config.race == 1) or \
                    (config_talent.target in [8, 12] and self.__unit.config.race == 3) or \
                    (config_talent.target in [9, 13] and self.__unit.config.race == 2) or \
                    (config_talent.target == 14 and self.__unit.config.tp == 2) or \
                    (config_talent.target == 15 and self.__unit.config.tp == 1):
                self._add_talent_effect_to_unit(config_talent)

        self.__unit.final_calculate()

    def add_equipment_property(self):
        # 加上装备属性
        pass

    def get_self_talent_skill_ids(self):
        ids = []
        ids.extend(self.config.talent_skill)
        for i in range(0, self.step + 1):
            if self.config.steps[i].talent_skill:
                ids.append(self.config.steps[i].talent_skill)

        return ids

    def add_self_talent_effect(self, club):
        """

        :param club:
        :type club: AbstractClub
        """
        # 天赋影响
        for tid in self.get_self_talent_skill_ids():
            config_talent = ConfigTalentSkill.get(tid)
            if config_talent.target == 1:
                # 选手自身
                self.self_talent_ids.append(tid)
            elif config_talent.target == 2:
                # 上阵所有选手
                for s in club.formation_staffs:
                    s.self_talent_ids.append(tid)
            elif config_talent.target == 3:
                # 上阵所有人族选手
                for s in club.get_formation_terran_staffs():
                    s.self_talent_ids.append(tid)
            elif config_talent.target == 4:
                # 上阵所有虫族选手
                for s in club.get_formation_zerg_staffs():
                    s.self_talent_ids.append(tid)
            elif config_talent.target == 5:
                # 上阵所有神族选手
                for s in club.get_formation_protoss_staffs():
                    s.self_talent_ids.append(tid)

            # 因为选手的带的兵也会随时变化，所以这里就直接把和兵相关的 天赋 记录下来
            # 这样就不用更换了兵种后再来判断天赋影响
            elif config_talent.target == 6:
                # 选手自身携带的任意兵种
                self.self_talent_ids.append(tid)
            elif config_talent.target == 7:
                # 选手自身携带的人族兵种
                self.self_talent_ids.append(tid)
            elif config_talent.target == 8:
                # 选手自身携带的虫族并种
                self.self_talent_ids.append(tid)
            elif config_talent.target == 9:
                # 选手自身携带的神族并种
                self.self_talent_ids.append(tid)

            elif config_talent.target == 10:
                # 所有选手所有任意兵种
                for s in club.formation_staffs:
                    s.self_talent_ids.append(tid)
            elif config_talent.target == 11:
                # 所有选手所有人族兵种
                for s in club.formation_staffs:
                    s.self_talent_ids.append(tid)
            elif config_talent.target == 12:
                # 所有选手所有虫族兵种
                for s in club.formation_staffs:
                    s.self_talent_ids.append(tid)
            elif config_talent.target == 13:
                # 所有选手所有神族兵种
                for s in club.formation_staffs:
                    s.self_talent_ids.append(tid)
            elif config_talent.target == 14:
                # 敌我上阵的所有空中兵种
                for s in club.formation_staffs:
                    s.self_talent_ids.append(tid)
            elif config_talent.target == 15:
                # 敌我上阵的所有地面兵种
                for s in club.formation_staffs:
                    s.self_talent_ids.append(tid)
            else:
                raise RuntimeError("Unknown talent {0} target {1}".format(tid, config_talent.target))

    def add_other_talent_effects(self, effect_ids):
        # NOTE 这个方法必须在 club 里调用。
        # 因为 可能有 要加给 敌方 的 talents
        # 这里如果给敌方加，就重复了
        for eid in effect_ids:
            config_talent = ConfigTalentSkill.get(eid)
            # if config_talent.target == 1:
            #     # 外部加成的天赋， 如果是选手自身，那么该是哪一个选手？
            #     # 所以这是错误情况
            #     raise RuntimeError("AbstractStaff.add_other_talent_effects. effect_id: {0} target is 1".format(eid))

            if config_talent.target in [1, 2, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] or \
                    (config_talent.target == 3 and self.config.race == 1) or \
                    (config_talent.target == 4 and self.config.race == 3) or \
                    (config_talent.target == 5 and self.config.race == 2):
                self.other_talent_ids.append(eid)
            else:
                raise RuntimeError("Unknown talent {0} target {1}".format(eid, config_talent.target))

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
        self.__unit.crit_multiple += config.unit_crit_multiple
        self.__unit.hurt_addition_to_terran += config.unit_hurt_addition_to_terran
        self.__unit.hurt_addition_to_protoss += config.unit_hurt_addition_to_protoss
        self.__unit.hurt_addition_to_zerg += config.unit_hurt_addition_to_zerg

        self.__unit.hurt_addition_by_terran += config.unit_hurt_addition_by_terran
        self.__unit.hurt_addition_by_protoss += config.unit_hurt_addition_by_protoss
        self.__unit.hurt_addition_by_zerg += config.unit_hurt_addition_by_zerg

        self.__unit.final_hurt_addition += config.unit_final_hurt_addition
        self.__unit.final_hurt_reduce += config.unit_final_hurt_reduce

        # 不能在这里 calculate
        # 如果是多个效果要加到unit上，这儿就会重复增加属性
        # self.__unit.calculate()

    @property
    def power(self):
        if not self.__unit:
            return 0

        # 属性参考战斗力计算表
        hp = (self.manage * 2 * math.pow(self.__unit.config.operation, 0.75) + self.__unit.hp) * \
             (1 + self.__unit.hp_percent)

        attack = (self.attack * 1 * math.pow(self.__unit.config.operation, 0.75) + self.__unit.attack) * \
                 (1 + self.__unit.attack_percent)

        defense = (self.defense * 1 * math.pow(self.__unit.config.operation, 0.75) + self.__unit.defense) * \
                  (1 + self.__unit.defense_percent)

        unit_amount = self.operation / self.__unit.config.operation
        t1 = attack * math.pow(unit_amount, 0.65) * self.__unit.attack_speed * \
             (1 + self.__unit.hit_rate - 0.9 + self.__unit.crit_rate * (self.__unit.crit_multiple - 1) * 0.7 +
              self.__unit.hurt_addition_to_terran * 0.2 + self.__unit.hurt_addition_to_zerg * 0.2 +
              self.__unit.hurt_addition_to_protoss * 0.2)

        t2 = (defense * math.pow(unit_amount, 0.65) * 0.5 + hp * unit_amount * 0.15) * \
             (1 + self.__unit.dodge_rate + self.__unit.toughness_rate -
              self.__unit.hurt_addition_by_terran * 0.2 -
              self.__unit.hurt_addition_by_protoss * 0.2 -
              self.__unit.hurt_addition_by_zerg * 0.2)

        return int(t1 + t2)

    def is_initial_state(self):
        # type: () -> bool
        if self.level != 1:
            return False

        if self.step != 0:
            return False

        if self.get_initial_star() != self.star:
            return False

        if self.level_exp > 0 or self.star_exp > 0:
            return False

        return True

    def get_initial_star(self):
        return (ConfigItemNew.get(self.oid).quality - 1) * 10

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
        msg.qianban_ids.extend(self.active_qianban_ids)

        return msg


class AbstractClub(object):
    __slots__ = [
        'server_id', 'char_id',
        'id', 'name', 'manager_name', 'flag', 'level',
        'exp', 'gold', 'diamond', 'crystal', 'gas', 'renown',
        'formation_staffs',

        # 给对手要加的天赋
        'talents_for_rival',
    ]

    def __init__(self):
        self.server_id = None
        self.char_id = None

        self.id = 0
        self.name = ""
        self.manager_name = ""
        self.flag = 0
        self.level = 1
        self.exp = 0
        self.gold = 0
        self.diamond = 0
        self.crystal = 0
        self.gas = 0
        self.renown = 0
        self.formation_staffs = []
        """:type: list[AbstractStaff]"""

        self.talents_for_rival = []

    def load_staffs(self, **kwargs):
        raise NotImplementedError()

    def get_formation_terran_staffs(self):
        return [s for s in self.formation_staffs if s.config.race == 1]

    def get_formation_protoss_staffs(self):
        return [s for s in self.formation_staffs if s.config.race == 2]

    def get_formation_zerg_staffs(self):
        return [s for s in self.formation_staffs if s.config.race == 3]

    @property
    def power(self):
        p = 0
        for s in self.formation_staffs:
            p += s.power

        return p

    def get_talents_ids_for_rival(self):
        # club instance 并没有缓存起来
        # 所以 staff.talent_effects 里如果给 club 添加了 talents_for_rival
        # 那么当时上下文销毁了，这些talents_for_rival就没有了
        # 所以这里要每次都重新获取
        ids = []
        for s in self.formation_staffs:
            for i in s.self_talent_ids:
                if ConfigTalentSkill.get(i).target in [14, 15]:
                    ids.append(i)

        return self.talents_for_rival + ids

    def add_talent_effects(self, talent_effect_ids):
        for i in talent_effect_ids:
            config = ConfigTalentSkill.get(i)
            if config.target in [14, 15]:
                self.talents_for_rival.append(i)

        for s in self.formation_staffs:
            s.add_other_talent_effects(talent_effect_ids)

    def add_temporary_talent_effects(self):
        # 添加临时天赋
        from core.tower import get_tower_talent_effects
        if not self.char_id:
            return

        effects = get_tower_talent_effects(self.server_id, self.char_id)
        if not effects:
            return

        self.add_talent_effects(effects)

    def add_rival_talent_effects(self, talent_effect_ids):
        # 添加来自对方的天赋效果
        for s in self.formation_staffs:
            s.add_other_talent_effects(talent_effect_ids)

    def make_temporary_staff_calculate(self):
        for s in self.formation_staffs:
            s.calculate()
            # no make cache

    def make_protomsg(self):
        msg = MessageClub()
        # 因为NPC的ID是UUID，所以这里为了统一，club的ID 都是 str
        msg.id = str(self.id)
        msg.name = self.name
        msg.manager = self.manager_name
        msg.flag = self.flag
        msg.level = self.level
        msg.exp = self.exp
        msg.gold = self.gold
        msg.diamond = self.diamond
        msg.crystal = self.crystal
        msg.gas = self.gas
        msg.renown = self.renown
        msg.power = self.power

        return msg
