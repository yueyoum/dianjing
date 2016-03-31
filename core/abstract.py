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


class AbstractStaff(object):
    __slots__ = [
        'server_id', 'char_id', 'id', 'oid', 'level', 'step', 'star', 'level_exp', 'star_exp',
        'active_qianban_ids',

        'equip_mouse', 'equip_keyboard', 'equip_monitor', 'equip_decoration',
        'attack', 'defense', 'manage', 'operation',
        'attack_percent', 'defense_percent', 'manage_percent', 'operation_percent',

        'unit_id',
        'position',
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

    @property
    def power(self):
        # TODO
        return 0

    def make_protomsg(self):
        fields = get_protocol_field_names(MessageStaff)
        msg = MessageStaff()
        for f in fields:
            setattr(msg, f, getattr(self, f))

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
        """:type: dict[int, AbstractStaff]"""

        self.match_staffs = []
        """:type: list[int]"""

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
