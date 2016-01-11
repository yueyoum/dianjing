# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       package
Date Created:   2015-07-20 23:44
Description:

"""

from config.base import ConfigBase

class Package(object):
    __slots__ = ['id', 'tp',

                 'attr_mode', 'attr_random_amount', 'attr_random_value',

                 'caozuo',
                 'baobing',
                 'jingying',
                 'zhanshu',

                 'biaoyan',
                 'yingxiao',

                 'zhimingdu',
                 'staff_exp',

                 'item_mode', 'item_random_amount',

                 'gold', 'diamond',
                 'club_renown',

                 'items',
                 'staff_cards',
                 ]
    
    def __init__(self):
        self.id = 0
        self.tp = 0

        self.attr_mode = 0
        self.attr_random_amount = 0
        self.attr_random_value = 0
        
        self.caozuo = []
        self.baobing = []
        self.jingying = []
        self.zhanshu = []

        self.biaoyan = []
        self.yingxiao = []

        self.zhimingdu = []
        self.staff_exp = []

        self.item_mode = []
        self.item_random_amount = []
        self.gold = []
        self.diamond = []
        
        self.club_renown = []

        self.items = []
        self.staff_cards = []


class ConfigPackage(ConfigBase):
    EntityClass = Package
    INSTANCES = {}
    FILTER_CACHE = {}


    @classmethod
    def get(cls, id):
        """

        :rtype : Package
        """
        return super(ConfigPackage, cls).get(id)
