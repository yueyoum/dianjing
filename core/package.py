# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       package
Date Created:   2015-07-20 23:49
Description:

"""

import base64
import random

from core.base import STAFF_ATTRS
from config import ConfigPackage

from protomsg.package_pb2 import (
    Drop as MsgDrop,
    TrainingItem as MsgTrainingItem
)

class PackageBase(object):
    __slots__ = STAFF_ATTRS + [
        'gold', 'diamond',
        'staff_exp', 'club_renown',
        'trainings',
    ]

    ATTRS = STAFF_ATTRS

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
        self.trainings = []

    @property
    def attrs(self):
        return {k: getattr(self, k) for k in self.ATTRS}


    @classmethod
    def generate(cls, pid):
        """

        :rtype : PackageBase
        """

        def set_value(attr, values):
            if not values:
                return

            low, high = values
            new_value = getattr(p, attr) + random.randint(low, high)
            setattr(p, attr, new_value)

        config = ConfigPackage.get(pid)

        p = cls()

        # 训练(道具)
        p.trainings = config.trainings

        # 软妹币，钻石，经验，荣耀
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


    @classmethod
    def new(cls, **kwargs):
        p = cls()
        for k, v in kwargs.iteritems():
            setattr(p, k, v)

        return p


class Drop(PackageBase):
    FIELDS = ['gold', 'diamond',
        'staff_exp', 'club_renown',
        'trainings']

    def make_protomsg(self):
        msg = MsgDrop()

        for attr in self.FIELDS:
            if attr != 'trainings':
                msg_item = msg.resources.add()
                msg_item.resource_id = attr
                msg_item.value = getattr(self, attr)


        for tid, amount in self.trainings:
            msg_training = msg.trainings.add()
            msg_training.id = tid
            msg_training.amount = amount

        return msg


    def dumps(self):
        data = self.make_protomsg().SerializeToString()
        return base64.b64encode(data)


    @classmethod
    def loads(cls, data):
        data = base64.b64decode(data)
        msg = MsgDrop()
        msg.ParseFromString(data)

        p = cls()

        for item in msg.resources:
            setattr(p, item.resource_id, item.value)


        for tr in msg.trainings:
            p.trainings.append((tr.id, tr.amount))

        return p


class TrainingItem(PackageBase):
    FIELDS = STAFF_ATTRS + ['staff_exp',]

    def make_protomsg(self):
        msg = MsgTrainingItem()

        for attr in self.FIELDS:
            value = getattr(self, attr)
            if not value:
                continue

            msg_resources = msg.resources.add()
            msg_resources.resource_id = attr
            msg_resources.value = value

        return msg

    def dumps(self):
        data = self.make_protomsg().SerializeToString()
        return base64.b64encode(data)

    @classmethod
    def loads(cls, data):
        """

        :rtype : TrainingItem
        """
        data = base64.b64decode(data)
        msg = MsgTrainingItem()
        msg.ParseFromString(data)

        p = cls()

        for item in msg.resources:
            setattr(p, item.resource_id, item.value)

        return p
