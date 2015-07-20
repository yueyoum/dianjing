# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       package
Date Created:   2015-07-20 23:49
Description:

"""

import random

from config import ConfigPackage

class Package(object):
    __slots__ = [
        'jingong', 'qianzhi', 'xintai', 'baobing',
        'fangshou', 'yunying', 'yishi', 'caozuo',
        'gold', 'diamond',
        'staff_exp', 'club_renown',
    ]

    ATTRS = [
        'jingong', 'qianzhi', 'xintai', 'baobing',
        'fangshou', 'yunying', 'yishi', 'caozuo',
    ]

    def __init__(self):
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

    @classmethod
    def generate(cls, pid):
        """

        :rtype : Package
        """

        def set_value(attr, values):
            if not values:
                return

            low, high = values
            new_value = getattr(p, attr) + random.randint(low, high)
            setattr(p, attr, new_value)

        config = ConfigPackage.get(pid)

        p = cls()

        set_value('gold', config.gold)
        set_value('diamond', config.diamond)
        set_value('staff_exp', config.staff_exp)
        set_value('club_renown', config.club_renown)

        if config.attr_mode == 1:
            # 不加成属性
            return p

        if config.attr_mode == 2:
            # 完全随机
            for i in range(config.attr_random_amount):
                attr = random.choice(cls.ATTRS)
                set_value(attr, config.attr_random_value)

            return p


        selected_attrs = [attr for attr in cls.ATTRS if getattr(config, attr)]

        if config.attr_mode == 4:
            # 设定的属性
            for attr in selected_attrs:
                set_value(attr, getattr(config, attr))

            return p

        # 从设定的属性中随机
        for i in range(config.attr_random_amount):
            attr = random.choice(selected_attrs)
            set_value(attr, getattr(config, attr))

        return p


