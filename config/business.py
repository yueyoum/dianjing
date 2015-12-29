# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       shop
Date Created:   2015-10-26 15:12
Description:

"""

from config.base import ConfigBase

class Shop(object):
    __slots__ = [
        'id', 'unlock_type', 'unlock_value', 'goods', 'goods_max_amount',
        'sells_per_hour',
        'mail_title', 'mail_content',
    ]

    def __init__(self):
        self.id = 0
        self.unlock_type = 0
        self.unlock_value = 0
        self.goods = 0
        self.goods_max_amount = 0
        self.sells_per_hour = 0
        self.mail_title = ''
        self.mail_content = ''


class Sponsor(object):
    __slots__ = [
        'id', 'condition', 'income', 'total_days',
        'mail_title', 'mail_content',
    ]
    
    def __init__(self):
        self.id = 0
        self.condition = 0
        self.income = 0
        self.total_days = 0
        self.mail_title = ''
        self.mail_content = ''


class ConfigBusinessShop(ConfigBase):
    EntityClass = Shop
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype : Shop
        """
        return super(ConfigBusinessShop, cls).get(_id)


class ConfigBusinessSponsor(ConfigBase):
    EntityClass = Sponsor
    INSTANCES = {}
    FILTER_CACHE = {}
    
    @classmethod
    def get(cls, _id):
        """

        :rtype : Sponsor
        """
        return super(ConfigBusinessSponsor, cls).get(_id)
