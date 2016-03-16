# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       abstract
Date Created:   2015-07-15 14:22
Description:

"""

import math
from itertools import chain

from core.qianban import QianBanContainer
from config import ConfigStaffLevel
from protomsg.club_pb2 import Club as MessageClub
from protomsg.staff_pb2 import Staff as MessageStaff

STAFF_BASE_ATTRS = [
    'luoji',
    'minjie',
    'lilun',
    'wuxing',
    'meili',
]

STAFF_SECONDARY_ATTRS = [
    'caozuo',
    'baobing',
    'jingying',
    'zhanshu',

    'biaoyan',
    'yingxiao'
]

SECONDARY_PROPERTY_TABLE = {
    'caozuo': [('minjie', 1)],
    'baobing': [('luoji', 1)],
    'jingying': [('lilun', 0.5)],
    'zhanshu': [('wuxing', 0.5)],

    'biaoyan': [('meili', 1)],
    'yingxiao': [('wuxing', 0.5), ('lilun', 0.5)]
}


class AbstractStaff(object):
    __slots__ = [
        'server_id', 'char_id', 'id', 'race', 'level', 'exp', 'status', 'quality', 'star',
        'skills', 'skills_detail',
        'active_qianban_ids',

        'luoji',
        'minjie',
        'lilun',
        'wuxing',
        'meili',

        'caozuo',
        'jingying',
        'baobing',
        'zhanshu',

        'biaoyan',
        'yingxiao',

        'zhimingdu',

        'equipments',

        'unit_id',
        'position',
    ]

    def __init__(self, *args, **kwargs):
        self.server_id = 0
        self.char_id = 0

        self.id = 0
        self.race = 0
        self.level = 0
        self.exp = 0
        self.status = 0
        self.quality = 0
        self.star = 0

        self.skills = {}
        self.skills_detail = {}
        self.active_qianban_ids = []

        self.luoji = 0
        self.minjie = 0
        self.lilun = 0
        self.wuxing = 0
        self.meili = 0

        self.caozuo = 0
        self.jingying = 0
        self.baobing = 0
        self.zhanshu = 0

        self.biaoyan = 0
        self.yingxiao = 0

        self.zhimingdu = 0

        self.equipments = []
        """:type: list[core.item.Equipment]"""

        self.unit_id = 0
        self.position = -1

    def calculate_secondary_property(self):
        for sp, info in SECONDARY_PROPERTY_TABLE.iteritems():
            value = 0
            for fp, param in info:
                value += getattr(self, fp) * param * (6 * math.pow(1.15, self.level) + 1 * self.level)

            setattr(self, sp, int(value))

    def strengthen(self, multiple):
        self.luoji *= multiple
        self.minjie *= multiple
        self.lilun *= multiple
        self.wuxing *= multiple
        self.meili *= multiple

        self.calculate_secondary_property()

    @property
    def power(self):
        p = 0
        for attr in STAFF_SECONDARY_ATTRS:
            p += getattr(self, attr)

        return int(p)

    def make_protomsg(self):
        msg = MessageStaff()

        msg.id = self.id
        msg.level = self.level
        msg.cur_exp = self.exp
        msg.max_exp = ConfigStaffLevel.get(self.level).exp[self.quality]
        msg.status = self.status
        msg.star = self.star
        msg.power = self.power

        msg.luoji = int(self.luoji)
        msg.minjie = int(self.minjie)
        msg.lilun = int(self.lilun)
        msg.wuxing = int(self.wuxing)
        msg.meili = int(self.meili)

        msg.caozuo = int(self.caozuo)
        msg.jingying = int(self.jingying)
        msg.baobing = int(self.baobing)
        msg.zhanshu = int(self.zhanshu)

        msg.biaoyan = int(self.biaoyan)
        msg.yingxiao = int(self.yingxiao)

        msg.zhimingdu = int(self.zhimingdu)

        for equip in self.equipments:
            msg_item = msg.items.add()
            msg_item.MergeFrom(equip.make_protomsg())

        for k, v in self.skills.iteritems():
            msg_skill = msg.skills.add()
            msg_skill.id = k
            msg_skill.level = v
            msg_skill.locked = self.skills_detail.get(k, {}).get('locked', 0)
            msg_skill.upgrade_end_at = self.skills_detail.get(k, {}).get('upgrade_end_at', 0)

        return msg


class AbstractClub(object):
    __slots__ = [
        'id', 'name', 'manager_name', 'flag', 'level',
        'renown', 'vip', 'gold', 'diamond', 'crystal', 'gas',
        'staffs', 'match_staffs', #'tibu_staffs',
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

        self.match_staffs = []  # int
        # self.tibu_staffs = []  # int

        self.policy = 1
        self.opened_slots = 6
        self.max_slots = 6

    def all_match_staffs(self):
        # 所有上阵员工
        # staffs = []
        # staffs.extend([i for i in self.match_staffs if i != 0])
        # staffs.extend([i for i in self.tibu_staffs if i != 0])
        #
        # return staffs
        return self.match_staffs

    def qianban_affect(self):
        qc = QianBanContainer(self.all_match_staffs())
        # for i in chain(self.match_staffs, self.tibu_staffs):
        for i in self.match_staffs:
            if i == 0:
                continue

            qc.affect(self.staffs[i])

    def match_staffs_ready(self):
        # return len(self.match_staffs) == 5 and all([i != 0 for i in self.match_staffs])
        return True

    def change_staff_strengthen(self, multiple):
        for s in self.staffs.values():
            s.strengthen(multiple)

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

        # match_staffs = self.match_staffs[:]
        # while len(match_staffs) < 6:
        #     match_staffs.append(0)
        #
        # tibu_staffs = self.tibu_staffs[:]
        # while len(tibu_staffs) < 5:
        #     tibu_staffs.append(0)

        # for i in chain(match_staffs, tibu_staffs):
        for i in self.match_staffs:
            msg_match_staff = msg.match_staffs.add()
            if i == 0:
                msg_match_staff.id = 0
                msg_match_staff.level = 0
                msg_match_staff.unit_id = 0
                msg_match_staff.position = 0
            else:
                msg_match_staff.id = i
                msg_match_staff.level = self.staffs[i].level
                msg_match_staff.qianban.extend(self.staffs[i].active_qianban_ids)
                msg_match_staff.unit_id = self.staffs[i].unit_id
                msg_match_staff.position = self.staffs[i].position

        return msg
