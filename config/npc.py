# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       npc
Date Created:   2015-07-22 17:07
Description:

"""

import random

from config.base import ConfigBase

class NPC(object):
    __slots__ = [
        'id',
        'league',
        'jingong_low', 'jingong_high',
        'qianzhi_low', 'qianzhi_high',
        'xintai_low', 'xintai_high',
        'baobing_low', 'baobing_high',
        'fangshou_low', 'fangshou_high',
        'yunying_low', 'yunying_high',
        'yishi_low', 'yishi_high',
        'caozuo_low', 'caozuo_high',
        'skill_low', 'skill_high',

        'name',
        'manager_name',
    ]

    def __init__(self):
        self.id = 0
        self.league = 0
        self.jingong_low = 0
        self.jingong_high = 0
        self.qianzhi_low = 0
        self.qianzhi_high = 0
        self.xintai_low = 0
        self.xintai_high = 0
        self.baobing_low = 0
        self.baobing_high = 0
        self.fangshou_low = 0
        self.fangshou_high = 0
        self.yunying_low = 0
        self.yunying_high = 0
        self.yishi_low = 0
        self.yishi_high = 0
        self.caozuo_low = 0
        self.caozuo_high = 0
        self.skill_low = 0
        self.skill_high = 0

        self.name = ""
        self.manager_name = ""



class ConfigNPC(ConfigBase):
    CLUB_NAMES = []
    MANAGER_NAMES = []

    EntityClass = NPC
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, id):
        """

        :rtype : NPC
        """
        return super(ConfigNPC, cls).get(id)

    @classmethod
    def initialize_club_names(cls, fixture):
        for f in fixture:
            cls.CLUB_NAMES.append(f["fields"]["name"])

    @classmethod
    def initialize_manager_name(cls, fixture):
        for f in fixture:
            cls.MANAGER_NAMES.append(f["fields"]["name"])

    @classmethod
    def get_club_names(cls):
        return cls.CLUB_NAMES[:]

    @classmethod
    def get_manager_names(cls):
        return cls.MANAGER_NAMES[:]


    @classmethod
    def random_npcs(cls, amount, league_level=1):
        from config import ConfigStaff
        from config import ConfigClubFlag

        flags = ConfigClubFlag.INSTANCES.keys()

        values = cls.filter(league=league_level).values()

        npcs = []
        while len(npcs) < amount:
            v = random.choice(values)

            npc = {}
            npc['club_name'] = random.choice(cls.CLUB_NAMES)
            npc['club_flag'] = random.choice(flags)
            npc['manager_name'] = random.choice(cls.MANAGER_NAMES)
            staffs = []

            staff_ids = ConfigStaff.random_ids(5)
            for i in range(5):
                staffs.append({
                    'id': staff_ids[i],
                    'jingong': random.randint(v.jingong_low, v.jingong_high),
                    'qianzhi': random.randint(v.qianzhi_low, v.qianzhi_high),
                    'xintai': random.randint(v.xintai_low, v.xintai_high),
                    'baobing': random.randint(v.baobing_low, v.baobing_high),
                    'fangshou': random.randint(v.fangshou_low, v.fangshou_high),
                    'yunying': random.randint(v.yunying_low, v.yunying_high),
                    'yishi': random.randint(v.yishi_low, v.yishi_high),
                    'caozuo': random.randint(v.caozuo_low, v.caozuo_high),
                    'skill_level': random.randint(v.skill_low, v.skill_high)
                })

            npc['staffs'] = staffs

            npcs.append(npc)

        return npcs
