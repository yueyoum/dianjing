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
        'jingong', 'qianzhi', 'xintai', 'baobing', 'fangshou', 'yunying',
        'yishi', 'caozuo', 'zhimingdu',
        'skills',
        'active_qianban_ids',
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

        self.jingong = 0
        self.qianzhi = 0
        self.xintai = 0
        self.baobing = 0
        self.fangshou = 0
        self.yunying = 0
        self.yishi = 0
        self.caozuo = 0
        self.zhimingdu = 0

        self.skills = {}

        self.active_qianban_ids = []

    def make_protomsg(self):
        msg = MessageStaff()

        msg.id = self.id
        msg.level = self.level
        msg.cur_exp = self.exp
        msg.max_exp = ConfigStaffLevel.get(self.level).exp[self.quality]
        msg.status = self.status

        msg.jingong = int(self.jingong)
        msg.qianzhi = int(self.qianzhi)
        msg.xintai = int(self.xintai)
        msg.baobing = int(self.baobing)
        msg.fangshou = int(self.fangshou)
        msg.yunying = int(self.yunying)
        msg.yishi = int(self.yishi)
        msg.caozuo = int(self.caozuo)
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
