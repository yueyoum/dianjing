# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       package
Date Created:   2015-07-20 23:49
Description:

"""

import json
import random

from core.abstract import STAFF_SECONDARY_ATTRS
from config import ConfigPackage, ConfigItem

from protomsg.package_pb2 import (
    Drop as MsgDrop,
    Property as MsgProperty,
)

from protomsg.item_pb2 import (
    ITEM_STAFF_CARD
)


def set_package_value(obj, attr_name, values):
    if not values:
        return

    low, high = values
    new_value = getattr(obj, attr_name) + random.randint(low, high)
    setattr(obj, attr_name, new_value)


# 这个对应编辑器中的 Package
class PackageBase(object):
    """
    物品包基类
        基本字段包括:
            员工属性        STAFF_BASE_ATTRS
            所有属性        FIELDS
    """
    FIELDS = STAFF_SECONDARY_ATTRS + [
        'gold', 'diamond', 'staff_exp', 'club_renown',
    ]

    FULL_FIELDS = FIELDS + ['items', 'staffs', 'staff_cards']

    def __init__(self):
        self.caozuo = 0  # 员工 - 操作
        self.baobing = 0  # 员工 - 暴兵
        self.jingying = 0  # 员工 - 经营
        self.zhanshu = 0  # 员工 - 战术

        self.biaoyan = 0  # 员工 - 表演
        self.yingxiao = 0  # 员工 - 营销

        self.zhimingdu = 0  # 员工 - 知名度
        self.staff_exp = 0

        self.gold = 0  # 角色 - 金币/软妹币
        self.diamond = 0  # 角色 - 钻石
        self.club_renown = 0  # 角色 - 俱乐部声望

        self.items = []  # 角色 - 物品
        self.staffs = []
        self.staff_cards = []

    def __str__(self):
        data = {}
        for attr in self.FULL_FIELDS:
            value = getattr(self, attr)
            if value:
                data[attr] = value

        return json.dumps(data)

    @classmethod
    def generate(cls, pid):
        raise NotImplementedError()

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

    # 还有 items, staffs, staff_cards

    @classmethod
    def generate(cls, pid):
        """

        :rtype: Drop
        """
        config = ConfigPackage.get(pid)
        assert config.tp == 2

        p = cls()
        set_package_value(p, 'gold', config.gold)
        set_package_value(p, 'diamond', config.diamond)
        set_package_value(p, 'club_renown', config.club_renown)

        if config.item_mode == 1:
            p.items = config.items
            p.staffs = config.staffs
            p.staff_cards = config.staff_cards
        else:
            all_stuffs = []
            for i in config.items:
                all_stuffs.append(('item', i))
            for i in config.staffs:
                all_stuffs.append(('staff', i))
            for i in config.staff_cards:
                all_stuffs.append(('staff_cards', i))

            for i in range(config.item_random_amount):
                # TODO more check
                _type, _data = random.choice(all_stuffs)
                if _type == 'item':
                    p.items.append(_data)
                elif _type == 'staff':
                    p.staffs.append(_data)
                elif _type == 'staff_cards':
                    p.staff_cards.append(_data)

        return p

    def make_protomsg(self):
        msg = MsgDrop()

        for attr in self.FIELDS:
            value = getattr(self, attr)
            if not value:
                continue

            msg_item = msg.resources.add()
            msg_item.resource_id = attr
            msg_item.value = value

        for _id, _amount in self.items:
            msg_item = msg.items.add()
            msg_item.id = _id
            msg_item.amount = _amount
            msg_item.tp = ConfigItem.get(_id).tp

        if self.staffs:
            msg.staffs.extend(self.staffs)

        for _id, _amount in self.staff_cards:
            msg_item = msg.items.add()
            msg_item.id = _id
            msg_item.amount = _amount
            msg_item.tp = ITEM_STAFF_CARD

        return msg

    def to_json(self):
        data = {}
        for attr in self.FIELDS:
            value = getattr(self, attr)
            if not value:
                continue

            data[attr] = value

        if self.items:
            data['items'] = self.items

        if self.staffs:
            data['staffs'] = self.staffs

        if self.staff_cards:
            data['staff_cards'] = self.staff_cards

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
    FIELDS = STAFF_SECONDARY_ATTRS + ['staff_exp']

    @classmethod
    def generate(cls, pid):
        """

        :rtype : Property
        """
        config = ConfigPackage.get(pid)
        assert config.tp == 1

        p = cls()

        active_attrs = {}
        for attr in cls.FIELDS:
            value = getattr(config, attr)
            if value:
                active_attrs[attr] = value

        active_attrs = active_attrs.items()

        if config.attr_mode == 1:
            # 设定的属性
            for k, v in active_attrs:
                set_package_value(p, k, v)

            return p

        if config.attr_mode == 2:
            # 从设定的属性中随机
            for i in range(config.attr_random_amount):
                k, v = random.choice(active_attrs)
                set_package_value(p, k, v)

            return p

        if config.attr_mode == 3:
            # 完全随机
            for i in range(config.attr_random_amount):
                attr = random.choice(STAFF_SECONDARY_ATTRS)
                value = random.choice(config.attr_random_value)
                setattr(p, attr, value)

            return p

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
        raise Exception("Property no need dump to json")

    @classmethod
    def loads_from_json(cls, data):
        raise Exception("Property no need load from json")
