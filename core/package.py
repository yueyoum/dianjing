# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       package
Date Created:   2015-07-20 23:49
Description:

"""

import json
import random

from core.base import STAFF_ATTRS
from config import ConfigPackage

from protomsg.package_pb2 import (
    Drop as MsgDrop,
    Property as MsgProperty,
)


# 这个对应编辑器中的 Package
class PackageBase(object):
    ATTRS = STAFF_ATTRS
    FIELDS = ATTRS + [
        'staff_exp', 'gold', 'diamond', 'club_renown', 'ladder_score', 'league_score',
    ]
    # fields also contains trainings

    def __init__(self):
        self.jingong = 0  # 员工 - 进攻
        self.qianzhi = 0  # 员工 - 牵制
        self.xintai = 0  # 员工 - 心态
        self.baobing = 0  # 员工 - 暴兵
        self.fangshou = 0  # 员工 - 防守
        self.yunying = 0  # 员工 - 运营
        self.yishi = 0  # 员工 - 意识
        self.caozuo = 0  # 员工 - 操作
        self.staff_exp = 0  # 员工 - 经验
        self.gold = 0  # 角色 - 金币/软妹币
        self.diamond = 0  # 角色 - 钻石
        self.club_renown = 0  # 角色 - 俱乐部声望
        self.ladder_score = 0  # 角色 - 天梯赛积分
        self.league_score = 0  # 角色 - 联赛积分
        self.trainings = []  # 角色 - 训练道具

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

        # 员工经验， 软妹币，钻石，荣耀，天梯赛积分，联赛积分
        set_value('staff_exp', config.staff_exp)
        set_value('gold', config.gold)
        set_value('diamond', config.diamond)
        set_value('club_renown', config.club_renown)
        set_value('ladder_score', config.ladder_score)
        set_value('league_score', config.league_score)

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

    def make_protomsg(self):
        raise NotImplementedError()

    def to_json(self):
        raise NotImplementedError()

    @classmethod
    def loads_from_json(cls, data):
        raise NotImplementedError()


# 对应只会给角色加的物品。 关卡掉落，奖励，邮件附件 这些
class Drop(PackageBase):
    FIELDS = ['gold', 'diamond', 'club_renown', 'ladder_score', 'league_score']
    # 还有 trainings

    def make_protomsg(self):
        msg = MsgDrop()

        for attr in self.FIELDS:
            value = getattr(self, attr)
            if not value:
                continue

            msg_item = msg.resources.add()
            msg_item.resource_id = attr
            msg_item.value = value

        for tid, amount in self.trainings:
            msg_training = msg.trainings.add()
            msg_training.id = tid
            msg_training.amount = amount

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
    FIELDS = STAFF_ATTRS + ['staff_exp']

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
            # 但是 StaffManager 的 update 接受的 exp
            # 所以这里把名字改一下
            if attr == 'staff_exp':
                attr = 'exp'
            data[attr] = value

        return data
