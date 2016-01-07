# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       item
Date Created:   2016-01-06 09-55
Description:

"""
from contextlib import contextmanager

from dianjing.exception import GameException

from core.mongo import MongoItem

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
        obj.unique_id = make_string_id()
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


# 简单物品 没有额外属性的，只记录个数量
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

        id_object = ItemId.make(oid, **kwargs)
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

        self.star = metadata['star']
        id_object = ItemId.parse(item_id)

        config = ConfigItem.get(id_object.oid)
        self.luoji = config.luoji
        self.minjie = config.minjie
        self.lilin = config.lilun
        self.wuxing = config.wuxing
        self.meili = config.meili

        # TODO secondary property
        self.caozuo = 99
        self.jingying = 99
        self.baobing = 99
        self.zhanshu = 99

        self.biaoyan = 99
        self.yingxiao = 99

        # TODO random property
        # metadata['luoji']

    def make_protomsg(self):
        id_object = ItemId.parse(self.item_id)

        msg = MsgItem()
        msg.id = self.item_id
        msg.oid = id_object.oid
        msg.tp = id_object.type_id

        msg.amount = 1
        msg.attr.star = self.star
        msg.attr.luoji = self.luoji
        msg.attr.minjie = self.minjie
        msg.attr.lilun = self.lilin
        msg.attr.wuxing = self.wuxing
        msg.attr.meili = self.meili
        msg.attr.caozuo = self.caozuo
        msg.attr.jingying = self.jingying
        msg.attr.baobing = self.baobing
        msg.attr.zhanshu = self.zhanshu
        msg.attr.biaoyan = self.biaoyan
        msg.attr.yingxiao = self.yingxiao

        return msg

    @classmethod
    def add(cls, server_id, char_id, type_id, oid, **kwargs):
        cls.check_type_id(type_id)

        amount = kwargs.get('amount', 1)

        notify = ItemNotify()
        notify.act = ACT_UPDATE

        for i in range(amount):
            id_object = ItemId.make(oid, **kwargs)
            item_id = id_object.to_string()

            # TODO real rule for generate an equipment
            metadata = {
                'star': 0,
                'luoji': 2
            }

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
