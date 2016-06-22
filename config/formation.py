# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       formation
Date Created:   2016-06-22 17-53
Description:

"""

from config.base import ConfigBase

class Slot(object):
    __slots__ = ['id', 'club_level']
    def __init__(self):
        self.id = 0
        self.club_level = 0


class ConfigFormationSlot(ConfigBase):
    EntityClass = Slot
    INSTANCES = {}
    """:type: dict[int, Slot]"""
    FILTER_CACHE = {}

    @classmethod
    def get_opened_slot_ids(cls, club_level):
        ids = []
        for k, v in cls.INSTANCES.iteritems():
            if club_level >= v.club_level:
                ids.append(k)

        ids.sort()
        return ids