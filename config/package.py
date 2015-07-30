# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       package
Date Created:   2015-07-20 23:44
Description:

"""

from config.base import ConfigBase

class Package(object):
    __slots__ = ['id', 'attr_mode', 'attr_random_amount', 'attr_random_value',
                 'jingong', 'qianzhi', 'xintai', 'baobing',
                 'fangshou', 'yunying', 'yishi', 'caozuo',
                 'gold', 'diamond',
                 'staff_exp', 'club_renown',
                 'trainings',
                 ]
    
    def __init__(self):
        self.id = None
        self.attr_mode = 0
        self.attr_random_amount = 0
        self.attr_random_value = 0
        
        self.jingong = 0
        self.qianzhi = 0
        self.xintai = 0
        self.baobing = 0
        self.fangshou = 0
        self.yunying = 0
        self.yishi = 0
        self.caozuo = 0
        
        self.gold = 0
        self.diamond = 0
        
        self.staff_exp = 0
        self.club_renown = 0

        self.trainings = []


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
