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

from utils.functional import make_short_string_id
from utils.message import MessagePipe

from config import ConfigItem, ConfigStaff, ConfigErrorMessage, ConfigEquipment

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.item_define_pb2 import (
    ITEM_DRINKS,
    ITEM_BADGE,
    ITEM_BUILDING_CERTIFICATE,
    ITEM_SHOP_GOODS,
    ITEM_TALENT_STONE,
    ITEM_STAFF_CARD,
    ITEM_EQUIPMENT,
    ITEM_BOX,

    Item as MsgItem,
)

from protomsg.item_pb2 import (
    ItemNotify,
    ItemRemoveNotify,
)

DRINKS_BY_QUALITY = {}
for __id, __drinks in ConfigItem.filter(tp=ITEM_DRINKS).iteritems():
    if __drinks.quality in DRINKS_BY_QUALITY:
        DRINKS_BY_QUALITY[__drinks.quality].append(__id)
    else:
        DRINKS_BY_QUALITY[__drinks.quality] = [__id]

BADGE_BY_TYPE_QUALITY = {}
BADGE_BY_QUALITY = {}
for __id, __badge in ConfigItem.filter(tp=ITEM_BADGE).iteritems():
    if __badge.group_id in BADGE_BY_TYPE_QUALITY:
        if __badge.quality in BADGE_BY_TYPE_QUALITY[__badge.group_id]:
            BADGE_BY_TYPE_QUALITY[__badge.group_id][__badge.quality].append(__id)
        else:
            BADGE_BY_TYPE_QUALITY[__badge.group_id][__badge.quality] = [__id]
    else:
        BADGE_BY_TYPE_QUALITY[__badge.group_id] = {__badge.quality: [__id]}

    if __badge.quality in BADGE_BY_QUALITY:
        BADGE_BY_QUALITY[__badge.quality].append(__id)
    else:
        BADGE_BY_QUALITY[__badge.quality] = [__id]

STONE_BY_SKILL_QUALITY = {}
STONE_BY_QUALITY = {}
for __id, __stone in ConfigItem.filter(tp=ITEM_TALENT_STONE).iteritems():
    if __stone.group_id in STONE_BY_SKILL_QUALITY:
        if __stone.quality in STONE_BY_SKILL_QUALITY[__stone.group_id]:
            STONE_BY_SKILL_QUALITY[__stone.group_id][__stone.quality].append(__id)
        else:
            STONE_BY_SKILL_QUALITY[__stone.group_id][__stone.quality] = [__id]
    else:
        STONE_BY_SKILL_QUALITY[__stone.group_id] = {__stone.quality: [__id]}

    if __stone.quality in STONE_BY_QUALITY:
        STONE_BY_QUALITY[__stone.quality].append(__id)
    else:
        STONE_BY_QUALITY[__stone.quality] = [__id]


class ItemId(object):
    def __init__(self):
        self.id = ""
        self.type_id = 0
        self.oid = 0
        self.unique_id = ""  # only for equipment
        self.star = 0  # only for staff card and equipment

    def to_string(self):
        if self.type_id == ITEM_EQUIPMENT:
            return "{0}:{1}:{2}:{3}".format(self.type_id, self.oid, self.star, self.unique_id)

        if self.type_id == ITEM_STAFF_CARD:
            return "{0}:{1}:{2}".format(self.type_id, self.oid, self.star)

        return "{0}:{1}".format(self.type_id, self.oid)

    @classmethod
    def make(cls, type_id, oid, **kwargs):
        """
        :param type_id: item type id
        :param oid: item original id (in the editor)
        :param kwargs: maybe has star=<int>
        :rtype: ItemId
        """
        obj = cls()
        obj.type_id = type_id
        obj.oid = oid

        if type_id == ITEM_EQUIPMENT:
            obj.unique_id = make_short_string_id()
        else:
            obj.unique_id = str(oid)

        obj.star = kwargs.get('star', 0)
        obj.id = obj.to_string()

        return obj

    @classmethod
    def parse(cls, item_id):
        """
        :param item_id: the unique item_id
        :rtype: ItemId
        """
        obj = cls()
        obj.id = item_id
        type_id, rest = item_id.split(':', 1)
        obj.type_id = int(type_id)

        if obj.type_id == ITEM_EQUIPMENT:
            oid, star, unique_id = rest.split(':')
            obj.oid = int(oid)
            obj.star = int(star)
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
    __slots__ = ['item_id', 'metadata', 'id_object']
    VALID_TYPE = []

    def __init__(self, item_id, metadata):
        self.item_id = item_id
        self.metadata = metadata

        self.id_object = ItemId.parse(item_id)

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
    def batch_get_metadata(cls, server_id, char_id, item_ids):
        projection = {i: 1 for i in item_ids}
        doc = MongoItem.db(server_id).find_one(
                {'_id': char_id},
                projection
        )

        if not doc:
            return {}

        return {i: doc.get(i, None) for i in item_ids}

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
    __slots__ = []

    VALID_TYPE = [
        ITEM_DRINKS,
        ITEM_BADGE,
        ITEM_BUILDING_CERTIFICATE,
        ITEM_SHOP_GOODS,
        ITEM_TALENT_STONE,
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
        """
        :param server_id: server id
        :param char_id: char id
        :param type_id: item type id
        :param oid: item original id. in the editor
        :param kwargs: maybe has amount=<int>
        :rtype: SimpleItem
        """
        cls.check_type_id(type_id)
        amount = kwargs.pop('amount', 1)

        id_object = ItemId.make(type_id, oid, **kwargs)
        item_id = id_object.id

        MongoItem.db(server_id).update_one({'_id': char_id}, {'$inc': {item_id: amount}})
        metadata = cls.get_metadata(server_id, char_id, item_id)

        obj = cls(item_id, metadata)

        notify = ItemNotify()
        notify.act = ACT_UPDATE
        notify_item = notify.items.add()
        notify_item.MergeFrom(obj.make_protomsg())

        MessagePipe(char_id).put(msg=notify)
        return obj

    @classmethod
    def remove(cls, server_id, char_id, item_id, amount=1):
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
            MessagePipe(char_id).put(msg=notify)


# 员工卡
class StaffCard(SimpleItem):
    __slots__ = []
    VALID_TYPE = [ITEM_STAFF_CARD]

    def make_protomsg(self):
        msg = MsgItem()
        msg.id = self.item_id
        msg.oid = self.id_object.oid
        msg.tp = self.id_object.type_id

        msg.amount = self.metadata
        msg.attr.star = self.id_object.star
        return msg


# 装备
class Equipment(BaseItem):
    __slots__ = ['luoji', 'minjie', 'lilun', 'wuxing', 'meili',
                 'caozuo', 'jingying', 'baobing', 'zhanshu',
                 'biaoyan', 'yingxiao',
                 ]

    VALID_TYPE = [ITEM_EQUIPMENT]

    def __init__(self, item_id, metadata):
        super(Equipment, self).__init__(item_id, metadata)

        self.luoji = 0
        self.minjie = 0
        self.lilun = 0
        self.wuxing = 0
        self.meili = 0
        self.caozuo = 0
        self.jingying = 0
        self.baobing = 0
        self.zhanshu = 0
        self.biaoyan = 0
        self.yingxiao = 0

        for attr in chain(STAFF_BASE_ATTRS, STAFF_SECONDARY_ATTRS):
            setattr(self, attr, metadata.get(attr, 0))

    def make_protomsg(self):
        msg = MsgItem()
        msg.id = self.item_id
        msg.oid = self.id_object.oid
        msg.tp = self.id_object.type_id

        msg.amount = 1
        msg.attr.star = self.id_object.star
        msg.attr.luoji = int(self.luoji)
        msg.attr.minjie = int(self.minjie)
        msg.attr.lilun = int(self.lilun)
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
    def _do_generate(cls, attrs, template, multiple=1.0):
        segment = random.choice(template)
        for name, value_range in segment:
            if name == 'primary':
                attr_names = STAFF_BASE_ATTRS
            elif name == 'secondary':
                attr_names = STAFF_SECONDARY_ATTRS
            else:
                attr_names = [name]

            value = int(random.randint(value_range[0], value_range[1]) * multiple)
            for an in attr_names:
                if an in attrs:
                    attrs[name] += value
                else:
                    attrs[name] = value

    @classmethod
    def generate(cls, oid, star):
        config = ConfigEquipment.get(oid)

        item_id = ItemId.make(ITEM_EQUIPMENT, oid).id
        attrs = {}

        if config.template_0:
            cls._do_generate(attrs, config.template_0)

        if star == 0:
            cls._do_generate(attrs, config.template_1)
        elif star == 1:
            cls._do_generate(attrs, config.template_1, multiple=1.5)
        elif star == 2:
            cls._do_generate(attrs, config.template_1, multiple=1.5)
            cls._do_generate(attrs, config.template_2)
        else:
            cls._do_generate(attrs, config.template_1, multiple=1.5)
            cls._do_generate(attrs, config.template_2, multiple=1.5)

        return item_id, attrs

    @classmethod
    def add(cls, server_id, char_id, type_id, oid, **kwargs):
        """
        :param server_id: server id
        :param char_id: char id
        :param type_id: item type id. MUST be ITEM_EQUIPMENT
        :param oid: equipment original id. in the editor
        :param kwargs: maybe has star=<int>
        :rtype: list[Equipment]
        """
        cls.check_type_id(type_id)

        star = kwargs.get('star', 0)
        amount = kwargs.get('amount', 1)

        objs = []

        for i in range(amount):
            notify = ItemNotify()
            notify.act = ACT_UPDATE

            item_id, metadata = cls.generate(oid, star)
            metadata['star'] = star

            MongoItem.db(server_id).update_one(
                    {'_id': char_id},
                    {'$set': {item_id: metadata}}
            )

            obj = cls(item_id, metadata)

            notify_item = notify.items.add()
            notify_item.MergeFrom(obj.make_protomsg())
            MessagePipe(char_id).put(msg=notify)

            objs.append(obj)
        return objs

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


def get_item_object(item_id, metadata):
    """
    :param item_id: the unique item id
    :param metadata: the data stored in db
    :rtype: BaseItem
    """
    id_object = ItemId.parse(item_id)

    if id_object.type_id == ITEM_EQUIPMENT:
        return Equipment(item_id, metadata)

    if id_object.type_id == ITEM_STAFF_CARD:
        return StaffCard(item_id, metadata)

    return SimpleItem(item_id, metadata)


class ItemManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoItem.exist(self.server_id, self.char_id):
            doc = MongoItem.document()
            doc['_id'] = self.char_id
            MongoItem.db(self.server_id).insert_one(doc)

    def check_exists(self, items, is_oid=False):
        # [(id, amount), (id, amount)]
        doc = MongoItem.db(self.server_id).find_one({'_id': self.char_id})
        for _id, amount in items:
            if is_oid:
                item_id = ItemId.make(ConfigItem.get(_id).tp, _id).id
            else:
                item_id = str(_id)

            metadata = doc.get(item_id, None)
            if metadata is None:
                raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_EXIST"))

            if isinstance(metadata, dict):
                # equipment, ignore _amount
                doc.pop(item_id)
            else:
                new_amount = metadata - amount
                if new_amount < 0:
                    raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_ENOUGH"))
                elif new_amount > 0:
                    doc[item_id] = new_amount
                else:
                    doc.pop(item_id)

    def get_all_items(self):
        """

        :rtype: list[BaseItem]
        """

        items = []
        doc = MongoItem.db(self.server_id).find_one({'_id': self.char_id}, {'_id': 0})
        for item_id, metadata in doc.iteritems():
            item = get_item_object(item_id, metadata)
            items.append(item)

        return items

    def add_item(self, oid, **kwargs):
        """
        :param oid: item oid
        :param kwargs: maybe has amount=<int> or star=<int>
        :rtype: list[BaseItem] | BaseItem
        一次add多个装备，返回的肯定是 多个 BaseItem
        但一次add多个其他简单物品，返回的只是一个 BaseItem
        """
        config = ConfigItem.get(oid)
        assert config is not None

        type_id = config.tp
        if type_id == ITEM_EQUIPMENT:
            return Equipment.add(self.server_id, self.char_id, type_id, oid, **kwargs)
        obj = SimpleItem.add(self.server_id, self.char_id, type_id, oid, **kwargs)
        return [obj]

    def add_staff_card(self, oid, star, amount=1):
        """
        :param oid: staff oid
        :param star: card star
        :param amount: amount
        :rtype: BaseItem
        """
        assert ConfigStaff.get(oid) is not None
        return StaffCard.add(self.server_id, self.char_id, ITEM_STAFF_CARD, oid, amount=amount, star=star)

    def remove_by_item_id(self, item_id, amount=1):
        id_object = ItemId.parse(item_id)
        if id_object.type_id == ITEM_EQUIPMENT:
            assert amount == 1
            Equipment.remove(self.server_id, self.char_id, item_id)
        elif id_object.type_id == ITEM_STAFF_CARD:
            StaffCard.remove(self.server_id, self.char_id, item_id, amount=amount)
        else:
            SimpleItem.remove(self.server_id, self.char_id, item_id, amount=amount)

    def get_simple_item_amount_by_oid(self, oid):
        config = ConfigItem.get(oid)
        assert config.tp != ITEM_EQUIPMENT

        item_id = ItemId.make(config.tp, oid).id
        metadata = SimpleItem.get_metadata(self.server_id, self.char_id, item_id)
        return metadata if metadata else 0

    def get_staff_card_amount_by_oid_and_star(self, oid, star):
        item_id = ItemId.make(ITEM_STAFF_CARD, oid, star=star).id
        metadata = StaffCard.get_metadata(self.server_id, self.char_id, item_id)
        return metadata if metadata else 0

    def remove_simple_item(self, oid, amount):
        config = ConfigItem.get(oid)
        assert config.tp != ITEM_EQUIPMENT

        item_id = ItemId.make(config.tp, oid).id
        self.remove_by_item_id(item_id, amount)

    def remove_staff_card(self, oid, star, amount):
        item_id = ItemId.make(ITEM_STAFF_CARD, oid, star=star).id
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

    def use(self, item_id, amount):
        id_object = ItemId.parse(item_id)
        if id_object.type_id != ITEM_BOX:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_USE"))

        if amount != 1:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_BOX_ONLY_USE_ONE"))

        self.remove_by_item_id(item_id, amount)
        return self.open_box(id_object.oid)

    def open_box(self, oid):
        config = ConfigItem.get(oid)
        drop = Drop.generate(config.value)

        message = "Open box {0}".format(oid)
        Resource(self.server_id, self.char_id).save_drop(drop, message=message)

        return drop

    def merge(self, item_ids):
        # 一次最多合成三个物品
        """
        :param item_ids: list of item ids
        :rtype: BaseItem
        """
        if len(item_ids) < 1 or len(item_ids) > 3:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        # check exists
        items = [(i, 1) for i in item_ids]
        self.check_exists(items)

        id_object_one = ItemId.parse(item_ids[0])
        if len(item_ids) == 1:
            if id_object_one.type_id == ITEM_EQUIPMENT:
                # 装备分解为同品质徽章
                return self.merge_equipment_1(id_object_one)
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        # len == 2
        id_object_two = ItemId.parse(item_ids[1])
        if len(item_ids) == 2:
            if id_object_one.type_id == ITEM_EQUIPMENT:
                if id_object_two.type_id == ITEM_EQUIPMENT:
                    # 两个装备 = 同装备star+1
                    return self.merge_equipment_2(id_object_one, id_object_two)
                raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

            if id_object_one.type_id == ITEM_STAFF_CARD:
                if id_object_two.type_id == ITEM_STAFF_CARD:
                    # 角色卡合成
                    return self.merge_staff_card_2(id_object_one, id_object_two)
                raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

            if id_object_one.type_id == ITEM_DRINKS:
                if id_object_two.type_id == ITEM_BADGE:
                    # 饮品 + 徽章 = 同品质徽章
                    return self.merge_badge_and_drinks_2(id_object_two, id_object_one)
                raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

            if id_object_one.type_id == ITEM_BADGE:
                if id_object_two.type_id == ITEM_DRINKS:
                    # 饮品 + 徽章 = 同品质徽章
                    return self.merge_badge_and_drinks_2(id_object_one, id_object_two)
                if id_object_two.type_id == ITEM_BADGE:
                    # 两个相同徽章 = 品质+1同类徽章
                    return self.merge_badge_2(id_object_one, id_object_two)
                if id_object_two.type_id == ITEM_TALENT_STONE:
                    # 石头 + 徽章 = 品质+1随机石头
                    return self.merge_badge_and_stone_2(id_object_one, id_object_two)
                raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

            if id_object_one.type_id == ITEM_TALENT_STONE:
                if id_object_two.type_id == ITEM_BADGE:
                    return self.merge_badge_and_stone_2(id_object_two, id_object_one)
                raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        # len == 3
        id_object_three = ItemId.parse(item_ids[2])
        if id_object_one.type_id == ITEM_DRINKS:
            if id_object_two.type_id == ITEM_DRINKS and id_object_three.type_id == ITEM_DRINKS:
                # 三个同品质饮品 = 高一级随机饮品
                return self.merge_drinks_3(id_object_one, id_object_two, id_object_three)
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        if id_object_one.type_id == ITEM_BADGE:
            if id_object_two.type_id == ITEM_BADGE:
                if id_object_three.type_id == ITEM_BADGE:
                    # 三个同品质徽章 = 高一级随机徽章
                    return self.merge_badge_3(id_object_one, id_object_two, id_object_three)
                raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))
            if id_object_two.type_id == ITEM_TALENT_STONE:
                if id_object_three.type_id == ITEM_TALENT_STONE:
                    # 两个同种同品质石头 + 同品质徽章 = 高一级品质同种徽章
                    return self.merge_stone_stone_badge_3(id_object_two, id_object_three, id_object_one)
                raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        if id_object_one.type_id == ITEM_TALENT_STONE:
            if id_object_two.type_id == ITEM_TALENT_STONE:
                if id_object_three.type_id == ITEM_TALENT_STONE:
                    return self.merge_stone_3(id_object_one, id_object_two, id_object_three)
                if id_object_three.type_id == ITEM_BADGE:
                    return self.merge_stone_stone_badge_3(id_object_one, id_object_two, id_object_three)
                raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))
            if id_object_two.type_id == ITEM_BADGE:
                if id_object_three.type_id == ITEM_TALENT_STONE:
                    return self.merge_stone_stone_badge_3(id_object_one, id_object_three, id_object_two)
                raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

    def merge_staff_card_2(self, id_object_one, id_object_two):
        if id_object_one.id != id_object_two.id:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        # TODO max star
        if id_object_one.star >= 20:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        self.remove_by_item_id(id_object_one.id, 2)
        return self.add_staff_card(id_object_one.oid, id_object_one.star + 1)

    def merge_equipment_1(self, id_object):
        quality = ConfigItem.get(id_object.oid).quality
        oid = random.choice(BADGE_BY_QUALITY[quality])
        self.remove_by_item_id(id_object.id)
        return self.add_item(oid)

    def merge_equipment_2(self, id_object_one, id_object_two):
        if id_object_one.oid != id_object_two.oid:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        if id_object_one.star != id_object_two.star:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        if id_object_one.star >= 3:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        self.remove_by_item_id(id_object_one.id)
        self.remove_by_item_id(id_object_two.id)
        obj = self.add_item(id_object_one.oid, star=id_object_one.star + 1)
        return obj[0]

    def merge_badge_2(self, id_object_one, id_object_two):
        if id_object_one.oid != id_object_two.oid:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        config = ConfigItem.get(id_object_one.oid)
        quality = config.quality

        if quality + 1 not in BADGE_BY_TYPE_QUALITY[config.group_id]:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        oid = random.choice(BADGE_BY_TYPE_QUALITY[config.group_id][quality + 1])
        self.remove_by_item_id(id_object_one.id)
        self.remove_by_item_id(id_object_two.id)
        return self.add_item(oid)

    def merge_badge_and_drinks_2(self, badge_id_object, drinks_id_object):
        quality = ConfigItem.get(badge_id_object.oid).quality

        badges = BADGE_BY_QUALITY[quality][:]
        badges.remove(badge_id_object.oid)

        if not badges:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        oid = random.choice(badges)
        self.remove_by_item_id(badge_id_object.id)
        self.remove_by_item_id(drinks_id_object.id)
        return self.add_item(oid)

    def merge_badge_and_stone_2(self, badge_id_object, stone_id_object):
        badge_quality = ConfigItem.get(badge_id_object.oid).quality
        stone_quality = ConfigItem.get(stone_id_object.oid).quality

        if badge_quality != stone_quality:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        stones = STONE_BY_QUALITY[stone_quality][:]
        stones.remove(stone_id_object.oid)

        if not stones:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        oid = random.choice(stones)
        self.remove_by_item_id(badge_id_object.id)
        self.remove_by_item_id(stone_id_object.id)
        return self.add_item(oid)

    def merge_drinks_3(self, id_object_one, id_object_two, id_object_three):
        quality_one = ConfigItem.get(id_object_one.oid).quality
        quality_two = ConfigItem.get(id_object_two.oid).quality
        quality_three = ConfigItem.get(id_object_three.oid).quality

        if not (quality_one == quality_two == quality_three):
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        if quality_one + 1 not in DRINKS_BY_QUALITY:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        oid = random.choice(DRINKS_BY_QUALITY[quality_one + 1])

        self.remove_by_item_id(id_object_one.id)
        self.remove_by_item_id(id_object_two.id)
        self.remove_by_item_id(id_object_three.id)
        return self.add_item(oid)

    def merge_badge_3(self, id_object_one, id_object_two, id_object_three):
        quality_one = ConfigItem.get(id_object_one.oid).quality
        quality_two = ConfigItem.get(id_object_two.oid).quality
        quality_three = ConfigItem.get(id_object_three.oid).quality

        if not (quality_one == quality_two == quality_three):
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        if quality_one + 1 not in BADGE_BY_QUALITY:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        oid = random.choice(BADGE_BY_QUALITY[quality_one + 1])
        self.remove_by_item_id(id_object_one.id)
        self.remove_by_item_id(id_object_two.id)
        self.remove_by_item_id(id_object_three.id)
        return self.add_item(oid)

    def merge_stone_3(self, id_object_one, id_object_two, id_object_three):
        quality_one = ConfigItem.get(id_object_one.oid).quality
        quality_two = ConfigItem.get(id_object_two.oid).quality
        quality_three = ConfigItem.get(id_object_three.oid).quality

        if not (quality_one == quality_two == quality_three):
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        if quality_one + 1 not in STONE_BY_QUALITY:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        oid = random.choice(STONE_BY_QUALITY[quality_one + 1])
        self.remove_by_item_id(id_object_one.id)
        self.remove_by_item_id(id_object_two.id)
        self.remove_by_item_id(id_object_three.id)

        return self.add_item(oid)

    def merge_stone_stone_badge_3(self, stone_one_id_object, stone_two_id_object, badge_id_object):
        stone_one_config = ConfigItem.get(stone_one_id_object.oid)
        stone_two_config = ConfigItem.get(stone_two_id_object.oid)

        if stone_one_config.group_id != stone_two_config.group_id:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        if stone_one_config.quality != stone_two_config.quality:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        badge_config = ConfigItem.get(badge_id_object.oid)
        if stone_one_config.quality != badge_config.quality:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        if stone_one_config.quality + 1 not in STONE_BY_SKILL_QUALITY[stone_one_config.group_id]:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_MERGE_BAD_REQUEST"))

        oid = random.choice(STONE_BY_SKILL_QUALITY[stone_one_config.group_id][stone_one_config.quality + 1])

        self.remove_by_item_id(stone_one_id_object.id)
        self.remove_by_item_id(stone_two_id_object.id)
        self.remove_by_item_id(badge_id_object.id)
        return self.add_item(oid)

    def send_notify(self):
        items = self.get_all_items()

        notify = ItemNotify()
        notify.act = ACT_INIT

        for item in items:
            notify_item = notify.items.add()
            notify_item.MergeFrom(item.make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)
