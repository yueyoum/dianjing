# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       party
Date Created:   2016-09-19 11:53
Description:

"""
import random
from config.base import ConfigBase

class PartyLevel(object):
    __slots__ = ['id', 'need_union_level', 'need_diamond',
                 'talent_skills', 'item_id',
                 'mail_title',
                 'mail_content',
                 'buy_one',
                 'buy_two',
                 ]

    def __init__(self):
        self.id = 0
        self.need_union_level = 0
        self.need_diamond = 0
        self.talent_skills = []
        self.item_id = 0
        self.mail_title = ''
        self.mail_content = ''
        self.buy_one = 0
        self.buy_two = 0


class PartyBuyItem(object):
    __slots__ = [
        'id', 'name', 'cost', 'reward'
    ]

    def __init__(self):
        self.id = 0
        self.name = ''
        self.cost = []
        self.reward = []

    def buy_result(self):
        return random.choice(self.reward)


class ConfigPartyLevel(ConfigBase):
    EntityClass = PartyLevel
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: PartyLevel
        """
        return super(ConfigPartyLevel, cls).get(_id)


class ConfigPartyBuyItem(ConfigBase):
    EntityClass = PartyBuyItem
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: PartyBuyItem
        """
        return super(ConfigPartyBuyItem, cls).get(_id)