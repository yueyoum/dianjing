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

        'caozuo', 'baobing', 'jingying', 'zhanshu',
        'skill_level',

        'name',
        'manager_name',
    ]

    def __init__(self):
        self.id = 0
        self.league = 0

        self.caozuo = []
        self.baobing = []
        self.jingying = []
        self.zhanshu = []
        self.skill_level = []

        self.name = ""
        self.manager_name = ""


class ConfigNPC(ConfigBase):
    CLUB_NAMES = []
    MANAGER_NAMES = []

    EntityClass = NPC
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype : NPC
        """
        return super(ConfigNPC, cls).get(_id)

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
        """:type: list[NPC]"""

        npcs = []

        club_names = cls.get_club_names()
        manager_names = cls.get_manager_names()
        club_name_used = set()
        manager_name_used = set()

        def _get_club_name():
            while True:
                if not club_names:
                    raise RuntimeError("not enough club name")

                name = random.choice(club_names)
                club_names.remove(name)
                if name not in club_name_used:
                    club_name_used.add(name)
                    return name

        def _get_manager_name():
            while True:
                if not manager_names:
                    raise RuntimeError("not enough manager name")

                name = random.choice(manager_names)
                manager_names.remove(name)
                if name not in manager_name_used:
                    manager_name_used.add(name)
                    return name

        while len(npcs) < amount:
            v = random.choice(values)
            """:type: NPC"""
            # 这里仅仅是获取NPC俱乐部配置，然后其他都是随机的，所以这里不用删除v

            npc = {}

            npc['club_name'] = _get_club_name()
            npc['manager_name'] = _get_manager_name()
            npc['club_flag'] = random.choice(flags)
            staffs = []

            staff_ids = ConfigStaff.random_ids(5)
            for i in range(5):
                # NPC staff 不用设置知名度属性，因为它对战斗无用
                staffs.append({
                    'id': staff_ids[i],
                    'caozuo': random.randint(v.caozuo[0], v.caozuo[1]),
                    'baobing': random.randint(v.baobing[0], v.baobing[1]),
                    'jingying': random.randint(v.jingying[0], v.jingying[1]),
                    'zhanshu': random.randint(v.zhanshu[0], v.zhanshu[1]),

                    'skill_level': random.randint(v.skill_level[0], v.skill_level[1])
                })

            npc['staffs'] = staffs
            npcs.append(npc)

        return npcs
