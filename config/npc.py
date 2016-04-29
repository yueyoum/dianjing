# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       npc
Date Created:   2016-04-29 01-20
Description:

"""

from core.abstract import AbstractClub, AbstractStaff
from config.base import ConfigBase

class _Staff(AbstractStaff):
    __slots__ = []
    def __init__(self, _id):
        super(_Staff, self).__init__()
        self.id = str(_id)
        self.oid = _id
        self.after_init()

class _Club(AbstractClub):
    __slots__ = ['npc_staffs']
    def __init__(self, _id, npc_staffs):
        super(_Club, self).__init__()
        self.id = _id
        self.flag = 1
        self.npc_staffs = npc_staffs

    def load_staffs(self, **kwargs):
        from core.unit import NPCUnit
        for pos, staff_id, unit_id in self.npc_staffs:
            s = _Staff(staff_id)
            s.formation_position = pos
            u = NPCUnit(unit_id, 0, 1)
            s.set_unit(u)
            s.calculate()
            self.formation_staffs.append(s)


class NPCFormation(object):
    __slots__ = ['id', 'staffs']
    def __init__(self):
        self.id = 0
        self.staffs = []

    def make_club(self):
        """

        :rtype: _Club
        """
        return _Club(self.id, self.staffs)


class ConfigNPCFormation(ConfigBase):
    EntityClass = NPCFormation
    INSTANCES = {}
    """:type: dict[int, NPCFormation]"""
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: _Club
        """
        return cls.INSTANCES[_id].make_club()

