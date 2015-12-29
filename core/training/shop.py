# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       shop
Date Created:   2015-11-02 10:26
Description:    网店

"""

import arrow

from dianjing.exception import GameException

from core.mongo import MongoTrainingShop
from core.staff import StaffManger
from core.package import Drop
from core.bag import BagItem
from core.resource import Resource
from core.mail import MailManager
from core.signals import training_shop_start_signal

from utils.message import MessagePipe
from utils.api import Timerd

from config import ConfigErrorMessage, ConfigBusinessShop, ConfigItem

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.training_pb2 import (
    TRAINING_SLOT_EMPTY,
    TRAINING_SLOT_NOT_OPEN,
    TRAINING_SLOT_TRAINING,

    TrainingShopNotify,
)

TRAINING_SHOP_CALLBACK = '/api/timerd/training/shop/'


class Shop(object):
    OPEN = 1
    NOT_OPEN = 2

    def __init__(self, server_id, char_id, _id, data=None):
        self.server_id = server_id
        self.char_id = char_id

        self.id = _id
        self.status = Shop.NOT_OPEN
        self.staff_id = 0
        self.sells_per_hour = 0
        self.start_at = 0
        self.end_at = 0
        self.key = ''
        self.goods = 0

        if data:
            self.status = Shop.OPEN
            self.staff_id = data.get('staff_id', 0)
            self.sells_per_hour = data.get('sells_per_hour', 0)
            self.start_at = data.get('start_at', 0)
            self.end_at = data.get('end_at', 0)
            self.key = data.get('key', '')
            self.goods = data.get('goods', 0)

        self.config = ConfigBusinessShop.get(self.id)
        self.sells_per_second = self.sells_per_hour / 3600.0

    def set_staff(self, staff_id):
        if self.staff_id:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_SHOP_IN_USE"))

        self.staff_id = staff_id
        # TODO
        self.sells_per_hour = 360
        if self.goods:
            self.start_at = arrow.utcnow().timestamp
            self._start()
            return True

        return False

    def add_goods(self):
        bi = BagItem(self.server_id, self.char_id)
        goods_amount = bi.current_amount(self.config.goods)

        if not goods_amount:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_EXIST"))

        if not self.staff_id:
            need_amount = self.config.goods_max_amount - self.goods
            if goods_amount > need_amount:
                goods_amount = need_amount

            bi.remove(self.config.goods, goods_amount)
            self.goods += goods_amount

            return False

        if self.key:
            Timerd.cancel(self.key)

        if self.goods:
            # 补货
            remained_amount = int((self.end_at - arrow.utcnow().timestamp) * self.sells_per_second)
            need_amount = self.config.goods_max_amount - remained_amount
            if goods_amount > need_amount:
                goods_amount = need_amount

            self.goods = remained_amount + goods_amount

        else:
            self.start_at = arrow.utcnow().timestamp
            if goods_amount > self.config.goods_max_amount:
                goods_amount = self.config.goods_max_amount

            self.goods = goods_amount

        with bi.remove_context(self.config.goods, goods_amount):
            self._start()

        return True

    def _start(self):
        assert self.start_at != 0

        total_seconds = int(round(self.goods * 1.0 / self.sells_per_second))
        self.end_at = self.start_at + total_seconds

        data = {
            'sid': self.server_id,
            'cid': self.char_id,
            'shop_id': self.id
        }

        self.key = Timerd.register(self.end_at, TRAINING_SHOP_CALLBACK, data)

    def cancel(self):
        if not self.staff_id or not self.goods:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_SHOP_CANNOT_CANCEL"))

        Timerd.cancel(self.key)
        sell_amount = int((arrow.utcnow().timestamp - self.start_at) * self.sells_per_second)
        return self._done(sell_amount)

    def finish(self):
        return self._done(self.goods)

    def _done(self, sell_amount):
        gold = ConfigItem.get(self.config.goods).value * sell_amount

        self.staff_id = 0
        self.sells_per_hour = 0
        self.sells_per_second = 0
        self.start_at = 0
        self.end_at = 0
        self.key = ''
        self.goods -= sell_amount

        drop = Drop()
        drop.gold = gold
        return drop

    def to_document(self):
        return {
            'staff_id': self.staff_id,
            'sells_per_hour': self.sells_per_hour,
            'start_at': self.start_at,
            'end_at': self.end_at,
            'key': self.key,
            'goods': self.goods,
        }

    def save(self):
        MongoTrainingShop.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'shops.{0}'.format(self.id): self.to_document()},
            upsert=True
        )


# 网店
class TrainingShop(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoTrainingShop.exist(self.server_id, self.char_id):
            for shop_id in ConfigBusinessShop.INSTANCES.keys():
                if ConfigBusinessShop.get(shop_id).unlock_type == 1:
                    # 无需解锁
                    Shop(self.server_id, self.char_id, shop_id).save()

    def staff_is_training(self, staff_id):
        doc = MongoTrainingShop.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'shops': 1}
        )

        for shop in doc['shops'].values():
            if shop.get('staff_id', 0) == staff_id:
                return True

        return False

    def trig_open_by_club_level(self, club_level):
        doc = MongoTrainingShop.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'shops': 1}
        )

        opened_shop_ids = []
        for shop_id in ConfigBusinessShop.INSTANCES.keys():
            if ConfigBusinessShop.get(shop_id).unlock_type != 2:
                continue

            if ConfigBusinessShop.get(shop_id).unlock_value > club_level:
                continue

            if str(shop_id) in doc['shops']:
                continue

            opened_shop_ids.append(shop_id)

        if opened_shop_ids:
            self.open(opened_shop_ids)

    def trig_open_by_vip_level(self, vip_level):
        doc = MongoTrainingShop.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'shops': 1}
        )

        opened_shop_ids = []
        for shop_id in ConfigBusinessShop.INSTANCES.keys():
            if ConfigBusinessShop.get(shop_id).unlock_type != 3:
                continue

            if ConfigBusinessShop.get(shop_id).unlock_value > vip_level:
                continue

            if str(shop_id) in doc['shops']:
                continue

            opened_shop_ids.append(shop_id)

        if opened_shop_ids:
            self.open(opened_shop_ids)

    def open(self, shop_ids):
        for i in shop_ids:
            Shop(self.server_id, self.char_id, i).save()

        self.send_notify(shop_ids=shop_ids)

    def get_shop(self, shop_id):
        """

        :rtype : Shop
        """
        doc = MongoTrainingShop.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'shops.{0}'.format(shop_id): 1}
        )

        try:
            data = doc['shops'][str(shop_id)]
            return Shop(self.server_id, self.char_id, shop_id, data)
        except KeyError:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_SHOP_NOT_OPEN"))

    def start(self, shop_id, staff_id):
        from core.training import TrainingExp, TrainingBroadcast

        if not StaffManger(self.server_id, self.char_id).has_staff(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        config = ConfigBusinessShop.get(shop_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_SHOP_NOT_EXIST"))

        # 不能同时进行
        if TrainingExp(self.server_id, self.char_id).staff_is_training(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_DOING_EXP"))

        if TrainingBroadcast(self.server_id, self.char_id).staff_is_training(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_DOING_BROADCAST"))

        doc = MongoTrainingShop.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'shops': 1}
        )

        for k, v in doc['shops'].iteritems():
            if v == staff_id:
                raise GameException(ConfigErrorMessage.get_error_id("TRAINING_SHOP_STAFF_IN_TRAINING"))

        shop = self.get_shop(shop_id)
        started = shop.set_staff(staff_id)
        shop.save()

        self.send_notify(shop_ids=[shop_id])

        if started:
            training_shop_start_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
                staff_id=staff_id,
            )

    def sell(self, shop_id):
        shop = self.get_shop(shop_id)
        started = shop.add_goods()
        shop.save()

        self.send_notify(shop_ids=[shop_id])

        if started:
            training_shop_start_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
                staff_id=shop.staff_id,
            )

    def cancel(self, shop_id):
        shop = self.get_shop(shop_id)
        drop = shop.cancel()
        shop.save()

        message = "Training Shop Cancel. {0}".format(shop_id)
        Resource(self.server_id, self.char_id).save_drop(drop, message=message)

        self.send_notify(shop_ids=[shop_id])
        return drop

    def callback(self, shop_id):
        shop = self.get_shop(shop_id)
        drop = shop.finish()
        shop.save()

        MailManager(self.server_id, self.char_id).add(
            shop.config.mail_title,
            shop.config.mail_content,
            attachment=drop.to_json()
        )

        self.send_notify(shop_ids=[shop_id])
        return drop

    def send_notify(self, shop_ids=None):
        if shop_ids:
            act = ACT_UPDATE
            projections = {'shops.{0}'.format(i): 1 for i in shop_ids}
        else:
            act = ACT_INIT
            projections = {'shops': 1}
            shop_ids = ConfigBusinessShop.INSTANCES.keys()
            shop_ids.sort()

        doc = MongoTrainingShop.db(self.server_id).find_one(
            {'_id': self.char_id},
            projections
        )

        notify = TrainingShopNotify()
        notify.act = act

        for i in shop_ids:
            notify_shop = notify.shop.add()
            notify_shop.id = i

            try:
                this_shop = doc['shops'][str(i)]
            except KeyError:
                notify_shop.status = TRAINING_SLOT_NOT_OPEN
                notify_shop.staff_id = 0
                notify_shop.sells_per_hour = 0
                notify_shop.start_at = 0
                notify_shop.end_at = 0
            else:
                shop_obj = Shop(self.server_id, self.char_id, i, this_shop)
                if shop_obj.staff_id:
                    notify_shop.status = TRAINING_SLOT_EMPTY
                else:
                    notify_shop.status = TRAINING_SLOT_TRAINING

                notify_shop.staff_id = shop_obj.staff_id
                notify_shop.sells_per_hour = shop_obj.sells_per_hour
                notify_shop.start_at = shop_obj.start_at
                notify_shop.end_at = shop_obj.end_at

        MessagePipe(self.char_id).put(msg=notify)
