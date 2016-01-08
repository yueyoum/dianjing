# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       item
Date Created:   2016-01-06 09-55
Description:

"""

import random
from itertools import chain
from contextlib import contextmanager

from dianjing.exception import GameException

from core.mongo import MongoItem
from core.abstract import STAFF_BASE_ATTRS, STAFF_SECONDARY_ATTRS
from core.package import Drop
from core.resource import Resource

from utils.functional import make_string_id
from utils.message import MessagePipe

from config import ConfigItem, ConfigStaff, ConfigErrorMessage

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.item_pb2 import (
    ITEM_TRAINING_EXPENDABLE,
    ITEM_SHOP_GOODS,
    ITEM_BUILDING_CERTIFICATE,
    ITEM_SKILL_TRAINING_BOOK,

    ITEM_EQUIPMENT,
    ITEM_STAFF_CARD,

    ITEM_BOX,

    ItemNotify,
    ItemRemoveNotify,
    Item as MsgItem,
)


class ItemId(object):
    def __init__(self):
        self.type_id = 0
        self.oid = 0
        self.unique_id = ""  # only for equipment
        self.star = 0  # only for staff card

    def to_string(self):
        if self.type_id == ITEM_EQUIPMENT:
            return "{0}:{1}:{2}".format(self.type_id, self.oid, self.unique_id)

        if self.type_id == ITEM_STAFF_CARD:
            return "{0}:{1}:{2}".format(self.type_id, self.oid, self.star)

        return "{0}:{1}".format(self.type_id, self.oid)

    @classmethod
    def make(cls, type_id, oid, **kwargs):
        """
        :param type_id: item type id
        :param oid: item original id (in the editor)
        :rtype: ItemId
        """
        obj = cls()
        obj.type_id = type_id
        obj.oid = oid

        if type_id == ITEM_EQUIPMENT:
            obj.unique_id = make_string_id()
        else:
            obj.unique_id = str(oid)

        obj.star = kwargs.get('star', 0)

        return obj

    @classmethod
    def parse(cls, item_id):
        """
        :param item_id: the unique item_id
        :rtype: ItemId
        """
        obj = cls()
        type_id, rest = item_id.split(':', 1)
        obj.type_id = int(type_id)

        if obj.type_id == ITEM_EQUIPMENT:
            oid, unique_id = rest.split(':')
            obj.oid = int(oid)
            obj.unique_id = unique_id
            return obj

        if obj.type_id == ITEM_STAFF_CARD:
            oid, star = rest.split(':')
            obj.oid = int(oid)
            obj.star = int(star)
            return obj

        obj.oid = int(rest)
        return obj


# 物品基类
class BaseItem(object):
    VALID_TYPE = []

    def __init__(self, item_id, metadata, **kwargs):
        self.item_id = item_id
        self.metadata = metadata
        self.kwargs = kwargs

    def make_protomsg(self):
        raise NotImplementedError()

    @classmethod
    def get_metadata(cls, server_id, char_id, item_id):
        doc = MongoItem.db(server_id).find_one(
                {'_id': char_id},
                {item_id: 1}
        )

        if not doc:
            return None

        return doc.get(item_id, None)

    @classmethod
    def add(cls, server_id, char_id, type_id, oid, **kwargs):
        raise NotImplementedError()

    @classmethod
    def remove(cls, server_id, char_id, item_id, **kwargs):
        raise NotImplementedError()

    @classmethod
    def check_type_id(cls, type_id):
        # 检查 物品类 方法传入的type_id 是否属于这个物品类
        assert type_id in cls.VALID_TYPE


# 简单物品 没有额外属性的，只记录数量
class SimpleItem(BaseItem):
    VALID_TYPE = [
        ITEM_TRAINING_EXPENDABLE,
        ITEM_SHOP_GOODS,
        ITEM_BUILDING_CERTIFICATE,
        ITEM_SKILL_TRAINING_BOOK,
        ITEM_BOX,
    ]

    def make_protomsg(self):
        id_object = ItemId.parse(self.item_id)

        msg = MsgItem()
        msg.id = self.item_id
        msg.oid = id_object.oid
        msg.tp = id_object.type_id

        msg.amount = self.metadata
        return msg

    @classmethod
    def add(cls, server_id, char_id, type_id, oid, **kwargs):
        cls.check_type_id(type_id)

        amount = kwargs.get('amount', 1)

        id_object = ItemId.make(type_id, oid, **kwargs)
        item_id = id_object.to_string()

        MongoItem.db(server_id).update_one({'_id': char_id}, {'$inc': {item_id: amount}})
        metadata = cls.get_metadata(server_id, char_id, item_id)

        obj = cls(item_id, metadata, **kwargs)

        notify = ItemNotify()
        notify.act = ACT_UPDATE
        notify_item = notify.items.add()
        notify_item.MergeFrom(obj.make_protomsg())

        MessagePipe(char_id).put(msg=notify)

    @classmethod
    def remove(cls, server_id, char_id, item_id, **kwargs):
        amount = kwargs.get('amount', 1)
        metadata = cls.get_metadata(server_id, char_id, item_id)
        if not metadata:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_EXIST"))

        if metadata < amount:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_ENOUGH"))

        new_amount = metadata - amount
        if new_amount == 0:
            MongoItem.db(server_id).update_one(
                    {'_id': char_id},
                    {'$unset': {item_id: 1}}
            )

            notify = ItemRemoveNotify()
            notify.ids.append(item_id)
            MessagePipe(char_id).put(msg=notify)
        else:
            MongoItem.db(server_id).update_one(
                    {'_id': char_id},
                    {'$set': {item_id: new_amount}}
            )

            metadata = cls.get_metadata(server_id, char_id, item_id)
            obj = cls(item_id, metadata)
            notify = ItemNotify()
            notify.act = ACT_UPDATE
            notify_item = notify.items.add()
            notify_item.MergeFrom(obj.make_protomsg())


# 员工卡
class StaffCard(SimpleItem):
    VALID_TYPE = [ITEM_STAFF_CARD]

    def make_protomsg(self):
        id_object = ItemId.parse(self.item_id)

        msg = MsgItem()
        msg.id = self.item_id
        msg.oid = id_object.oid
        msg.tp = id_object.type_id

        msg.amount = self.metadata
        msg.attr.star = self.kwargs['star']
        return msg


# 装备
class Equipment(BaseItem):
    VALID_TYPE = [ITEM_EQUIPMENT]

    def __init__(self, item_id, metadata):
        super(Equipment, self).__init__(item_id, metadata)

        self.luoji = 0
        self.minjie = 0
        self.lilin = 0
        self.wuxing = 0
        self.meili = 0
        self.caozuo = 0
        self.jingying = 0
        self.baobing = 0
        self.zhanshu = 0
        self.biaoyan = 0
        self.yingxiao = 0

        self.star = metadata['star']
        for attr in chain(STAFF_BASE_ATTRS, STAFF_SECONDARY_ATTRS):
            setattr(self, attr, metadata[attr])

    def make_protomsg(self):
        id_object = ItemId.parse(self.item_id)

        msg = MsgItem()
        msg.id = self.item_id
        msg.oid = id_object.oid
        msg.tp = id_object.type_id

        msg.amount = 1
        msg.attr.star = self.star
        msg.attr.luoji = int(self.luoji)
        msg.attr.minjie = int(self.minjie)
        msg.attr.lilun = int(self.lilin)
        msg.attr.wuxing = int(self.wuxing)
        msg.attr.meili = int(self.meili)
        msg.attr.caozuo = int(self.caozuo)
        msg.attr.jingying = int(self.jingying)
        msg.attr.baobing = int(self.baobing)
        msg.attr.zhanshu = int(self.zhanshu)
        msg.attr.biaoyan = int(self.biaoyan)
        msg.attr.yingxiao = int(self.yingxiao)

        return msg

    @classmethod
    def generate(cls, oid):
        config = ConfigItem.get(oid)

        attrs = {}
        for attr in STAFF_BASE_ATTRS:
            attrs[attr] = getattr(config, attr)
        for attr in STAFF_SECONDARY_ATTRS:
            attrs[attr] = 0

        item_id = ItemId.make(ITEM_EQUIPMENT, oid).to_string()

        # 随机一个二级属性
        attr = random.choice(STAFF_SECONDARY_ATTRS)
        value = random.randint(20, 50) * config.quality
        attrs[attr] += round(value, 2)

        # 所有二级属性
        for attr in STAFF_SECONDARY_ATTRS:
            value = random.randint(4, 10) * config.quality
            attrs[attr] += round(value, 2)

        # 随机一个一级属性
        attr = random.choice(STAFF_BASE_ATTRS)
        value = random.uniform(0.5, 0.8) * config.quality
        attrs[attr] += round(value, 2)

        # 所有一级属性
        for attr in STAFF_BASE_ATTRS:
            value = random.uniform(0.12, 0.2) * config.quality
            attrs[attr] += round(value, 2)

        return item_id, attrs

    @classmethod
    def add(cls, server_id, char_id, type_id, oid, **kwargs):
        cls.check_type_id(type_id)

        amount = kwargs.get('amount', 1)

        notify = ItemNotify()
        notify.act = ACT_UPDATE

        for i in range(amount):
            item_id, metadata = cls.generate(oid)
            metadata['star'] = kwargs.get('star', 0)

            MongoItem.db(server_id).update_one(
                    {'_id': char_id},
                    {'$set': {item_id: metadata}}
            )

            obj = cls(item_id, metadata)

            notify_item = notify.items.add()
            notify_item.MergeFrom(obj.make_protomsg())

        MessagePipe(char_id).put(msg=notify)

    @classmethod
    def remove(cls, server_id, char_id, item_id, **kwargs):
        metadata = cls.get_metadata(server_id, char_id, item_id)
        if not metadata:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_EXIST"))

        MongoItem.db(server_id).update_one(
                {'_id': char_id},
                {'$unset': {item_id: 1}}
        )

        notify = ItemRemoveNotify()
        notify.ids.append(item_id)
        MessagePipe(char_id).put(msg=notify)


class ItemManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoItem.exist(self.server_id, self.char_id):
            doc = MongoItem.document()
            doc['_id'] = self.char_id
            MongoItem.db(self.server_id).insert_one(doc)

    @staticmethod
    def get_item(item_id, metadata):
        """
        :param item_id: the unique item id
        :param metadata: the data stored in db
        :rtype: BaseItem
        """
        id_object = ItemId.parse(item_id)

        if id_object.type_id == ITEM_EQUIPMENT:
            return Equipment(item_id, metadata)

        if id_object.type_id == ITEM_STAFF_CARD:
            return StaffCard(item_id, metadata, star=id_object.star)

        return SimpleItem(item_id, metadata)

    def add_item(self, oid, amount):
        config = ConfigItem.get(oid)
        if not config:
            raise RuntimeError("no item {0}".format(oid))

        type_id = config.tp
        if type_id == ITEM_EQUIPMENT:
            Equipment.add(self.server_id, self.char_id, type_id, oid, amount=amount)
        else:
            SimpleItem.add(self.server_id, self.char_id, type_id, oid, amount=amount)

    def add_staff_card(self, oid, amount):
        if not ConfigStaff.get(oid):
            raise RuntimeError("no staff card {0}".format(oid))

        StaffCard.add(self.server_id, self.char_id, ITEM_STAFF_CARD, oid, amount=amount, star=0)

    def remove_by_item_id(self, item_id, amount):
        id_object = ItemId.parse(item_id)
        if id_object.type_id == ITEM_EQUIPMENT:
            Equipment.remove(self.server_id, self.char_id, item_id)
        elif id_object.type_id == ITEM_STAFF_CARD:
            StaffCard.remove(self.server_id, self.char_id, item_id, amount=amount)
        else:
            SimpleItem.remove(self.server_id, self.char_id, item_id, amount=amount)

    def get_simple_item_amount_by_oid(self, oid):
        config = ConfigItem.get(oid)
        assert config.tp != ITEM_EQUIPMENT

        item_id = ItemId.make(config.tp, oid).to_string()
        metadata = SimpleItem.get_metadata(self.server_id, self.char_id, item_id)
        return metadata if metadata else 0

    def check_simple_item_is_enough(self, data):
        for oid, amount in data:
            stock = self.get_simple_item_amount_by_oid(oid)
            if stock < amount:
                return False

        return True

    def get_staff_card_amount_by_oid_and_star(self, oid, star):
        item_id = ItemId.make(ITEM_STAFF_CARD, oid, star=star).to_string()
        metadata = StaffCard.get_metadata(self.server_id, self.char_id, item_id)
        return metadata if metadata else 0

    def remove_simple_item(self, oid, amount):
        config = ConfigItem.get(oid)
        assert config.tp != ITEM_EQUIPMENT

        item_id = ItemId.make(config.tp, oid).to_string()
        self.remove_by_item_id(item_id, amount)

    def remove_staff_card(self, oid, star, amount):
        item_id = ItemId.make(ITEM_STAFF_CARD, oid, star=star).to_string()
        self.remove_by_item_id(item_id, amount)

    @contextmanager
    def remove_simple_item_context(self, oid, amount):
        stock = self.get_simple_item_amount_by_oid(oid)
        if stock < amount:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_ENOUGH"))

        yield

        self.remove_simple_item(oid, amount)

    def sell(self, item_id, amount):
        id_object = ItemId.parse(item_id)

        if id_object.type_id == ITEM_STAFF_CARD:
            gold = 10
        else:
            config = ConfigItem.get(id_object.oid)
            gold = config.sell_gold
            if not gold:
                raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_SELL"))

        self.remove_by_item_id(item_id, amount)

        gold *= amount
        drop = Drop()
        drop.gold = gold

        if id_object.type_id == ITEM_STAFF_CARD:
            message = "Sell staff card {0}".format(id_object.oid)
        else:
            message = "Sell item {0}".format(id_object.oid)

        Resource(self.server_id, self.char_id).save_drop(drop, message=message)

    def open(self, item_id):
        pass

    def merge(self):
        pass

    def send_notify(self):
        doc = MongoItem.db(self.server_id).find_one({'_id': self.char_id}, {'_id': 0})

        notify = ItemNotify()
        notify.act = ACT_INIT

        for item_id, metadata in doc.iteritems():
            item = self.get_item(item_id, metadata)

            notify_item = notify.items.add()
            notify_item.MergeFrom(item.make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)
