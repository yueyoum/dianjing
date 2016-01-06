# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       item
Date Created:   2016-01-06 09-55
Description:

"""

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

    ItemNotify,
    ItemRemoveNotify,
    Item as MsgItem,
)

SIMPLE_TYPE = {
    ITEM_TRAINING_EXPENDABLE,
    ITEM_SHOP_GOODS,
    ITEM_BUILDING_CERTIFICATE,
    ITEM_SKILL_TRAINING_BOOK
}


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


class BaseItem(object):
    def __init__(self, item_id, metadata, **kwargs):
        self.item_id = item_id
        self.metadata = metadata
        self.kwargs = kwargs

    def make_protomsg(self):
        raise NotImplementedError()

    @classmethod
    def make_id_object(cls, type_id, oid, **kwargs):
        return ItemId.make(type_id, oid, **kwargs)

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


class SimpleItem(BaseItem):
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
        assert type_id != ITEM_EQUIPMENT

        amount = kwargs.get('amount', 1)

        id_object = cls.make_id_object(type_id, oid, **kwargs)
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


class StaffCard(SimpleItem):
    def make_protomsg(self):
        id_object = ItemId.parse(self.item_id)

        msg = MsgItem()
        msg.id = self.item_id
        msg.oid = id_object.oid
        msg.tp = id_object.type_id

        msg.amount = self.metadata
        msg.attr.star = self.kwargs['star']
        return msg


class Equipment(BaseItem):
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
        assert type_id == ITEM_EQUIPMENT

        amount = kwargs.get('amount', 1)

        notify = ItemNotify()
        notify.act = ACT_UPDATE

        for i in range(amount):
            # TODO real rule for generate an equipment
            id_object = cls.make_id_object(type_id, oid, **kwargs)
            item_id = id_object.to_string()

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

    def remove(self, item_id, amount):
        id_object = ItemId.parse(item_id)
        if id_object.type_id == ITEM_EQUIPMENT:
            Equipment.remove(self.server_id, self.char_id, item_id)
        elif id_object.type_id == ITEM_STAFF_CARD:
            StaffCard.remove(self.server_id, self.char_id, item_id, amount=amount)
        else:
            SimpleItem.remove(self.server_id, self.char_id, item_id, amount=amount)

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
