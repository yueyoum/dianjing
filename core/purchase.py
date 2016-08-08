# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       purchase
Date Created:   2016-08-02 17:25
Description:

"""

from dianjing.exception import GameException

from apps.purchase.models import Purchase as ModelPurchase

from core.mongo import MongoPurchase
from core.resource import ResourceClassification

from utils.message import MessagePipe
from utils.functional import make_string_id

from config import ConfigPurchaseYueka, ConfigPurchaseGoods, ConfigErrorMessage, ConfigItemUse

from protomsg.purchase_pb2 import PurchaseNotify, PURCHASE_DONE, PURCHASE_FAILURE, PURCHASE_WAITING

YUEKA_ID = 1001
FIRST_REWARD_ITEM_ID = -2

class Purchase(object):
    __slots__ = ['server_id', 'char_id', 'doc']
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.doc = MongoPurchase.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoPurchase.document()
            self.doc['_id'] = self.char_id
            MongoPurchase.db(self.server_id).insert_one(self.doc)

    def prepare(self, goods_id):
        if goods_id != YUEKA_ID:
            if not ConfigPurchaseGoods.get(goods_id):
                raise GameException(ConfigErrorMessage.get_error_id("PURCHASE_NOT_EXIST"))

        _id = make_string_id()
        ModelPurchase.objects.create(
            id=_id,
            server_id=self.server_id,
            char_id=self.char_id,
            goods_id=goods_id,
        )

        return _id

    def verify(self, receipt):
        try:
            p = ModelPurchase.objects.get(id=receipt)
            """:type: ModelPurchase"""
        except ModelPurchase.DoesNotExist:
            raise GameException(ConfigErrorMessage.get_error_id("PURCHASE_NOT_FOUND_RECEIPT"))

        if p.complete_timestamp:
            # TODO 根据不通平台和返回码 来确定是否成功
            if p.return_code == 0:
                status = PURCHASE_DONE
            else:
                status = PURCHASE_FAILURE
        else:
            status = PURCHASE_WAITING

        return p.goods_id, status

    def get_first_reward(self):
        if len(self.doc['goods']) != 1:
            raise GameException(ConfigErrorMessage.get_error_id("PURCHASE_NOT_FIRST_REWARD"))

        if self.doc.get('first_reward_got', False):
            raise GameException(ConfigErrorMessage.get_error_id("PURCHASE_FIRST_REWARD_HAS_GOT"))

        drop = ConfigItemUse.get(FIRST_REWARD_ITEM_ID).using_result()
        rc = ResourceClassification.classify(drop)
        rc.add(self.server_id, self.char_id)
        self.doc['first_reward_got'] = True

        MongoPurchase.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'first_reward_got': True
            }}
        )

        self.send_notify()
        return rc

    def send_notify(self):
        notify = PurchaseNotify()
        notify.yueka_remained_days = self.doc['yueka_remained_days']
        notify.first = len(self.doc['goods']) == 0

        drop = ConfigItemUse.get(FIRST_REWARD_ITEM_ID).using_result()
        rc = ResourceClassification.classify(drop)

        notify.first_reward.MergeFrom(rc.make_protomsg())
        notify.first_reward_got = self.doc.get('first_reward_got', False)

        MessagePipe(self.char_id).put(msg=notify)


def platform_callback(params):
    print params
