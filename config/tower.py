# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       tower
Date Created:   2016-05-04 17-58
Description:

"""

import random

from core.abstract import AbstractClub, AbstractStaff
from config.base import ConfigBase

class _Staff(AbstractStaff):
    __slots__ = []
    def __init__(self, _id):
        super(_Staff, self).__init__()
        from utils.functional import make_string_id
        self.id = make_string_id()
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


class TowerLevel(object):
    __slots__ = [
        'id', 'talent_id', 'staffs',
        'star_reward',
        'turntable',
        'sale_goods',
        'map_name',
    ]

    def __init__(self):
        self.id = 0
        self.talent_id = 0
        self.staffs = []
        self.star_reward = {}
        self.turntable = {}
        self.sale_goods = []
        self.map_name = ''

    def get_star_reward(self, star):
        return self.star_reward[str(star)]
    
    def get_turntable(self):
        table = {}
        if not self.turntable['3']:
            return table

        for k, v in self.turntable.iteritems():
            table[str(k)] = random.sample(v, 3)
        
        return table

    def get_sale_goods(self):
        if not self.sale_goods:
            return []

        prob = random.randint(1, 100)
        for id1, id2, _p in self.sale_goods:
            if _p >= prob:
                return [id1, id2]

        return []

    def make_club(self):
        """

        :rtype: _Club
        """
        return _Club(self.id, self.staffs)


class ResetCost(object):
    __slots__ = ['id', 'cost']
    def __init__(self):
        self.id = 0
        self.cost = 0


class ConfigTowerLevel(ConfigBase):
    EntityClass = TowerLevel
    INSTANCES = {}
    FILTER_CACHE = {}

    MAX_LEVEL = None

    @classmethod
    def initialize(cls, fixture):
        super(ConfigTowerLevel, cls).initialize(fixture)
        cls.MAX_LEVEL = max(cls.INSTANCES.keys())
    
    @classmethod
    def get(cls, _id):
        """

        :rtype: TowerLevel
        """
        return super(ConfigTowerLevel, cls).get(_id)


class ConfigTowerResetCost(ConfigBase):
    EntityClass = ResetCost
    INSTANCES = {}
    FILTER_CACHE = {}

    LIST = []


    @classmethod
    def initialize(cls, fixture):
        super(ConfigTowerResetCost, cls).initialize(fixture)
        for k, v in cls.INSTANCES.iteritems():
            cls.LIST.append((k, v.cost))

        cls.LIST.sort(key=lambda item: item[0], reverse=True)


    @classmethod
    def get_cost(cls, times):
        for k, v in cls.LIST:
            if times >= k:
                return v

        raise RuntimeError("ConfigTowerResetCost, Error times: {0}".format(times))


#######################
class StarReward(object):
    __slots__ = ['id', 'reward']
    def __init__(self):
        self.id = 0
        self.reward = 0

class ConfigTowerStarReward(ConfigBase):
    EntityClass = StarReward
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: StarReward
        """
        return super(ConfigTowerStarReward, cls).get(_id)


class RankReward(object):
    __slots__ = ['id', 'reward', 'mail_title', 'mail_content']
    def __init__(self):
        self.id = 0
        self.reward = []
        self.mail_title = ""
        self.mail_content = ""


class ConfigTowerRankReward(ConfigBase):
    EntityClass = RankReward
    INSTANCES = {}
    FILTER_CACHE = {}

    LIST = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigTowerRankReward, cls).initialize(fixture)
        cls.LIST = cls.INSTANCES.items()
        cls.LIST.sort(key=lambda item: item[0], reverse=True)


    @classmethod
    def get(cls, rank):
        """

        :rtype: RankReward
        """
        for k, v in cls.LIST:
            if rank >= k:
                return v

        raise RuntimeError("ConfigTowerRankReward, Error rank: {0}".format(rank))


######################
class SaleGoods(object):
    __slots__ = [
        'id', 'price_now', 'vip_need', 'item_id', 'amount'
    ]

    def __init__(self):
        self.id = 0
        self.price_now = 0
        self.vip_need = 0
        self.item_id = 0
        self.amount = 0

class ConfigTowerSaleGoods(ConfigBase):
    EntityClass = SaleGoods
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: SaleGoods
        """
        return super(ConfigTowerSaleGoods, cls).get(_id)