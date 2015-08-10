# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       npc
Date Created:   2015-07-22 17:07
Description:

"""

import copy
import random

from config.base import ConfigBase


class NPC(object):
    __slots__ = [
        'id',
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
    def random_npcs(cls, amount):
        names = random.sample(cls.CLUB_NAMES, amount)
        manager_names = random.sample(cls.MANAGER_NAMES, amount)

        npcs = []
        values = cls.INSTANCES.values()

        while len(npcs) < amount:
            v = random.choice(values)
            npcs.append(copy.copy(v))

        for index in range(amount):
            npcs[index].name = names[index]
            npcs[index].manager_name = manager_names[index]

        return npcs
