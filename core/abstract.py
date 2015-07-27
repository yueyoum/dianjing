# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       abstract
Date Created:   2015-07-15 14:22
Description:

"""

from itertools import chain
from protomsg.club_pb2 import Club as MessageClub



class AbstractStaff(object):
    def __init__(self, *args, **kwargs):
        self.id = None
        self.race = None
        self.level = None
        self.exp = None
        self.status = None

        self.jingong = None
        self.qianzhi = None
        self.xintai = None
        self.baobing = None
        self.fangshou = None
        self.yunying = None
        self.yishi = None
        self.caozuo = None

        self.skills = []



class AbstractClub(object):
    def __init__(self, *args, **kwargs):
        self.id = 0
        self.name = ""
        self.manager_name = ""
        self.flag = 0
        self.level = 0
        self.renown = 0
        self.vip = 0
        self.exp = 0
        self.gold = 0
        self.diamond = 0

        self.staffs = {} # Staff
        self.match_staffs = [] # int
        self.tibu_staffs = [] # int

        self.policy = 0


    def match_staffs_ready(self):
        return len(self.match_staffs) == 5


    def get_max_renown(self):
        return 0

    def make_protomsg(self):
        msg = MessageClub()
        msg.id = self.id
        msg.name = self.name
        msg.manager = self.manager_name
        msg.flag = self.flag
        msg.level = self.level
        msg.renown = self.renown
        msg.vip = self.vip
        msg.exp = self.exp
        msg.gold = self.gold
        msg.diamond = self.diamond
        msg.max_renown = self.get_max_renown()
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
                msg_match_staff.level = 0

        return msg
