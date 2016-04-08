# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       abstract
Date Created:   2015-07-15 14:22
Description:

"""

from core.qianban import QianBanContainer

from utils.protocol import get_protocol_field_names

from protomsg.club_pb2 import Club as MessageClub
from protomsg.staff_pb2 import Staff as MessageStaff
from protomsg.unit_pb2 import Unit as MessageUnit


class AbstractStaff(object):
    __slots__ = [
        'server_id', 'char_id', 'id', 'oid', 'level', 'step', 'star', 'level_exp', 'star_exp',
        'active_qianban_ids',

        'equip_mouse', 'equip_keyboard', 'equip_monitor', 'equip_decoration',
        'attack', 'defense', 'manage', 'operation',
        'attack_percent', 'defense_percent', 'manage_percent', 'operation_percent',

        'unit_id',
        'position',

        'quality',
    ]

    def __init__(self, *args, **kwargs):
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

        self.unit_id = 0
        self.position = -1

        self.quality = 0

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

        if self.star != (self.quality-1) * 10:
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
        msg.star_exp =self.star_exp
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
        'staffs', 'match_staffs',
        'policy',
        'opened_slots',
        'max_slots',
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

        self.staffs = {}  # Staff
        """:type: dict[string, AbstractStaff]"""

        self.match_staffs = []
        """:type: list[string]"""

        self.policy = 1
        self.opened_slots = 6
        self.max_slots = 6

    def all_match_staffs(self):
        return self.match_staffs

    def qianban_affect(self):
        qc = QianBanContainer(self.all_match_staffs())
        for i in self.match_staffs:
            if i == 0:
                continue

            qc.affect(self.staffs[i])

    def match_staffs_ready(self):
        return True

    def get_power(self):
        power = 0
        for staff_id in self.match_staffs:
            if not staff_id:
                continue
            power += self.staffs[staff_id].power

        return power

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
        msg.policy = self.policy

        msg.opened_slots = self.opened_slots
        msg.max_slots = self.max_slots

        for i in self.match_staffs:
            msg_match_staff = msg.match_staffs.add()
            msg_match_staff.id = i
            msg_match_staff.level = self.staffs[i].level
            msg_match_staff.qianban.extend(self.staffs[i].active_qianban_ids)
            msg_match_staff.unit_id = self.staffs[i].unit_id
            msg_match_staff.position = self.staffs[i].position

        return msg


class AbstractUnit(object):
    __slots__ = [
        'id', 'step', 'level',
        'tp', 'race', 'attack_tp', 'defense_tp', 'range_tp', 'skill_1', 'skill_2',
        'hp', 'hp_percent', 'attack', 'attack_percent', 'defense', 'defense_percent',
        'attack_speed', 'attack_speed_percent', 'attack_distance', 'attack_distance_percent',
        'move_speed', 'hit_rate', 'dodge_rate', 'crit_rate', 'crit_multi',
        'crit_anti_rate', 'append_attack_terran', 'append_attack_protoss', 'append_attack_zerg',
        'append_attacked_by_terran', 'append_attacked_by_protoss', 'append_attacked_by_zerg',
        'final_hurt_append', 'final_hurt_reduce',
    ]

    def __init__(self):
        self.id = 0 # NOTE: 就是本身的ID
        self.step = 0
        self.level = 0

        self.tp = 0
        self.race = 0
        self.attack_tp = 0
        self.defense_tp = 0
        self.range_tp = 0
        self.skill_1 = 0
        self.skill_2 = 0

        self.hp = 0
        self.hp_percent = 0.0
        self.attack = 0
        self.attack_percent = 0.0
        self.defense = 0
        self.defense_percent = 0.0
        self.attack_speed = 0
        self.attack_speed_percent = 0.0
        self.attack_distance = 0
        self.attack_distance_percent = 0.0
        self.move_speed = 0
        self.hit_rate = 0.0
        self.dodge_rate = 0.0
        self.crit_rate = 0.0
        self.crit_multi = 0.0
        self.crit_anti_rate = 0.0
        self.append_attack_terran = 0.0
        self.append_attack_protoss = 0.0
        self.append_attack_zerg = 0.0
        self.append_attacked_by_terran = 0.0
        self.append_attacked_by_protoss = 0.0
        self.append_attacked_by_zerg = 0.0
        self.final_hurt_append = 0
        self.final_hurt_reduce = 0

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
