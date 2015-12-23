# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       abstract
Date Created:   2015-07-15 14:22
Description:

"""

from itertools import chain

from core.qianban import QianBanContainer
from config import ConfigStaffLevel
from protomsg.club_pb2 import Club as MessageClub
from protomsg.staff_pb2 import Staff as MessageStaff


class AbstractStaff(object):
    __slots__ = [
        'server_id', 'char_id', 'id', 'race', 'level', 'exp', 'status', 'quality',
        'skills',
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
        'youmo',
        'yingxiao',
        'shichang',

        'zhimingdu',
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

        self.skills = {}
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
        self.youmo = 0
        self.yingxiao = 0
        self.shichang = 0

        self.zhimingdu = 0

    def calculate_secondary_property(self):
        # TODO
        self.caozuo = 100
        self.jingying = 100
        self.baobing = 100
        self.zhanshu = 100
        self.biaoyan = 100
        self.youmo = 100
        self.yingxiao = 100
        self.shichang = 100

    def strengthen(self, multiple):
        self.luoji += multiple
        self.minjie += multiple
        self.lilun += multiple
        self.wuxing += multiple
        self.meili += multiple

        self.calculate_secondary_property()

    def make_protomsg(self):
        msg = MessageStaff()

        msg.id = self.id
        msg.level = self.level
        msg.cur_exp = self.exp
        msg.max_exp = ConfigStaffLevel.get(self.level).exp[self.quality]
        msg.status = self.status

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
        msg.youmo = int(self.youmo)
        msg.yingxiao = int(self.yingxiao)
        msg.shichang = int(self.shichang)

        msg.zhimingdu = int(self.zhimingdu)

        return msg


class AbstractClub(object):
    __slots__ = [
        'id', 'name', 'manager_name', 'flag', 'level',
        'renown', 'vip', 'gold', 'diamond',
        'staffs', 'match_staffs', 'tibu_staffs',
        'policy'
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
        self.tibu_staffs = []  # int

        self.policy = 1

    def all_match_staffs(self):
        # 所有上阵员工
        staffs = []
        staffs.extend([i for i in self.match_staffs if i != 0])
        staffs.extend([i for i in self.tibu_staffs if i != 0])

        return staffs

    def qianban_affect(self):
        qc = QianBanContainer(self.all_match_staffs())
        for i in chain(self.match_staffs, self.tibu_staffs):
            if i == 0:
                continue

            qc.affect(self.staffs[i])

    def match_staffs_ready(self):
        return len(self.match_staffs) == 5 and all([i != 0 for i in self.match_staffs])

    def change_staff_strengthen(self, multiple):
        for s in self.staffs.values():
            s.strengthen(multiple)

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

        match_staffs = self.match_staffs[:]
        while len(match_staffs) < 5:
            match_staffs.append(0)

        tibu_staffs = self.tibu_staffs[:]
        while len(tibu_staffs) < 5:
            tibu_staffs.append(0)

        for i in chain(match_staffs, tibu_staffs):
            msg_match_staff = msg.match_staffs.add()
            if i == 0:
                msg_match_staff.id = 0
                msg_match_staff.level = 0
            else:
                msg_match_staff.id = i
                msg_match_staff.level = self.staffs[i].level
                msg_match_staff.qianban.extend(self.staffs[i].active_qianban_ids)

        return msg
