# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       package
Date Created:   2015-07-20 23:49
Description:

"""

import json
import random

from config import ConfigPackage

from protomsg.package_pb2 import (
    Drop as MsgDrop,
    Property as MsgProperty,
)

STAFF_BASE_ATTRS = [
    'luoji',
    'minjie',
    'lilun',
    'wuxing',
    'meili',
]


# 这个对应编辑器中的 Package
class PackageBase(object):
    """
    物品包基类
        基本字段包括:
            员工属性        STAFF_BASE_ATTRS
            所有属性        FIELDS
    """
    FIELDS = STAFF_BASE_ATTRS + [
        'gold', 'diamond', 'staff_exp', 'club_renown',
    ]

    FULL_FIELDS = FIELDS + ['trainings', 'items']

    def __init__(self):
        self.luoji = 0  # 员工 - 进攻
        self.minjie = 0  # 员工 - 牵制
        self.lilun = 0  # 员工 - 心态
        self.wuxing = 0  # 员工 - 暴兵
        self.meili = 0  # 员工 - 防守

        self.zhimingdu = 0  # 员工 - 知名度

        self.gold = 0  # 角色 - 金币/软妹币
        self.diamond = 0  # 角色 - 钻石
        self.staff_exp = 0  # 员工 - 经验
        self.club_renown = 0  # 角色 - 俱乐部声望

        self.trainings = []  # 角色 - 训练书
        self.items = []  # 角色 - 道具

    def __str__(self):
        data = {}
        for attr in self.FULL_FIELDS:
            value = getattr(self, attr)
            if value:
                data[attr] = value

        return json.dumps(data)

    @classmethod
    def generate(cls, pid):
        """

        :rtype : PackageBase
        """

        def set_value(attr_name, values):
            if not values:
                return

            low, high = values
            new_value = getattr(p, attr_name) + random.randint(low, high)
            setattr(p, attr_name, new_value)

        config = ConfigPackage.get(pid)

        p = cls()

        # 技能训练书
        p.trainings = config.trainings
        p.items = config.items

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
                attr = random.choice(STAFF_BASE_ATTRS)
                set_value(attr, config.attr_random_value)

            return p

        selected_attrs = [attr for attr in STAFF_BASE_ATTRS if getattr(config, attr)]

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

    def make_protomsg(self):
        raise NotImplementedError()

    def to_json(self):
        raise NotImplementedError()

    @classmethod
    def loads_from_json(cls, data):
        raise NotImplementedError()


# 对应只会给角色加的物品。 关卡掉落，奖励，邮件附件 这些
class Drop(PackageBase):
    FIELDS = ['gold', 'diamond', 'club_renown']
    # 还有 trainings, items

    def make_protomsg(self):
        msg = MsgDrop()

        for attr in self.FIELDS:
            value = getattr(self, attr)
            if not value:
                continue

            msg_item = msg.resources.add()
            msg_item.resource_id = attr
            msg_item.value = value

        for _id, _amount in self.trainings:
            msg_training = msg.trainings.add()
            msg_training.id = _id
            msg_training.amount = _amount

        for _id, _amount in self.items:
            msg_item = msg.items.add()
            msg_item.id = _id
            msg_item.amount = _amount

        return msg

    def to_json(self):
        data = {}
        for attr in self.FIELDS:
            value = getattr(self, attr)
            if not value:
                continue

            data[attr] = value

        if self.trainings:
            data['trainings'] = self.trainings

        if self.items:
            data['items'] = self.items

        return json.dumps(data)

    @classmethod
    def loads_from_json(cls, data):
        """

        :rtype : Drop
        """
        data = json.loads(data)
        obj = cls()

        for k, v in data.iteritems():
            setattr(obj, k, v)

        return obj


class Property(PackageBase):
    FIELDS = STAFF_BASE_ATTRS + ['staff_exp']

    def make_protomsg(self):
        msg = MsgProperty()

        for attr in self.FIELDS:
            value = getattr(self, attr)
            if not value:
                continue

            msg_item = msg.resources.add()
            msg_item.resource_id = attr
            msg_item.value = value

        return msg

    def to_dict(self):
        data = {}
        for attr in self.FIELDS:
            value = getattr(self, attr)
            if not value:
                continue

            # package 中员工经验是 staff_exp
            # 但是 StaffManager 的 update 接受的名字是 exp
            # 所以这里把名字改一下
            if attr == 'staff_exp':
                attr = 'exp'
            data[attr] = value

        return data

    def to_json(self):
        raise NotImplementedError()

    @classmethod
    def loads_from_json(cls, data):
        raise NotImplementedError()
