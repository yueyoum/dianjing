# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       purchase
Date Created:   2016-08-03 16:37
Description:

"""

from config.base import ConfigBase

class Goods(object):
    __slots__ = ['id', 'rmb', 'vip_exp', 'diamond', 'diamond_extra',
                 'ios_product_id']
    def __init__(self):
        self.id = 0
        self.rmb = 0
        self.vip_exp = 0
        self.diamond = 0
        self.diamond_extra = 0
        self.ios_product_id = ''

class Yueka(object):
    __slots__ = ['id', 'rmb', 'vip_exp', 'rewards', 'mail_title', 'mail_content',
                 'ios_product_id']
    def __init__(self):
        self.id = 0
        self.rmb = 0
        self.vip_exp = 0
        self.rewards = []
        self.mail_title = ''
        self.mail_content = ''
        self.ios_product_id = ''

class FirstReward(object):
    __slots__ = ['id', 'rewards']
    def __init__(self):
        self.id = 0
        self.rewards = []

class ConfigPurchaseGoods(ConfigBase):
    EntityClass = Goods
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: Goods
        """
        return super(ConfigPurchaseGoods, cls).get(_id)


class ConfigPurchaseYueka(ConfigBase):
    EntityClass = Yueka
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: Yueka
        """
        return super(ConfigPurchaseYueka, cls).get(_id)


class ConfigPurchaseFirstReward(ConfigBase):
    EntityClass = FirstReward
    INSTANCES = {}
    """:type: dict[int, FirstReward]"""
    FILTER_CACHE = {}

    @classmethod
    def get_reward(cls):
        return cls.INSTANCES.values()[0].rewards
