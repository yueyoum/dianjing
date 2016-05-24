# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       vip
Date Created:   2016-05-24 09-57
Description:

"""

from config.base import ConfigBase

class VIP(object):
    __slots__ = ['id', 'exp', 'item_id', 'diamond_original', 'diamond_now',
                 'challenge_reset_times',
                 'daily_dungeon_reset_times',
                 'tower_reset_times',
                 'arena_buy_times',
                 ]

    def __init__(self):
        self.id = 0
        self.exp = 0
        self.item_id = 0
        self.diamond_original = 0
        self.diamond_now = 0

        self.challenge_reset_times = 0
        self.daily_dungeon_reset_times = 0
        self.tower_reset_times = 0
        self.arena_buy_times = 0


class ConfigVIP(ConfigBase):
    EntityClass = VIP
    INSTANCES = {}
    FILTER_CACHE = {}
    
    @classmethod
    def get(cls, _id):
        """

        :rtype: VIP
        """
        return super(ConfigVIP, cls).get(_id)
