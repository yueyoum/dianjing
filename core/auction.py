# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       auction
Date Created:   2015-12-15 09:36
Description:    拍卖系统  电竞经理/员工系统/拍卖行

"""
import arrow
import math

from dianjing.exception import GameException

from core.staff import StaffManger
from core.mongo import MongoAuctionStaff, MongoBidding
from core.club import Club
from core.resource import Resource
from core.mail import MailManager
from core.package import Drop
from core.training import TrainingBroadcast, TrainingExp, TrainingProperty, TrainingShop
from core.lock import Lock, LockTimeOut

from utils.api import Timerd
from utils.functional import make_string_id

from config import ConfigErrorMessage, ConfigStaff

from protomsg.auction_pb2 import (
    AUCTION_HOURS_16,
    AUCTION_HOURS_24,
    AUCTION_HOURS_8,
    StaffAuctionBidingListNotify,
    StaffAuctionBidingRemoveNotify,
    StaffAuctionSellListNotify,
    StaffAuctionSellRemoveNotify,
    AuctionItem as MsgAuctionItem,
)

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from utils.message import MessagePipe

AUCTION_TYPE_HOURS = {
    AUCTION_HOURS_8: 8,
    AUCTION_HOURS_16: 16,
    AUCTION_HOURS_24: 24,
}

AUCTION_TYPE_TAX = {
    AUCTION_HOURS_8: 0.75,
    AUCTION_HOURS_16: 0.73,
    AUCTION_HOURS_24: 0.7
}

AUCTION_BIDDING_FAIL_TITLE = "竞标失败"
AUCTION_BIDDING_FAIL_CONTENT = "您竞拍{0}失败，金钱返还已经放入您的附件当中，请注意查收。"

AUCTION_BIDDING_SUCCESS_TITLE = "竞标成功"
AUCTION_BIDDING_SUCCESS_CONTENT = "您成功竞拍到{0}，已经放入您的附件当中，请注意查收。"

AUCTION_SUCCESS_TITLE = "拍卖成功"
AUCTION_SUCCESS_CONTENT = "您拍卖的{0}已经成功拍出，扣除税金后，总共获得{1}软妹币，已经放入您的附件当中，请注意查收"

AUCTION_FAIL_TITLE = "拍卖失败"
AUCTION_FAIL_CONTENT = "您拍卖的{0}超过拍卖时限而无人竞拍，已经流拍了。流拍的拍品已经放入您的附件当中，请注意查收"

AUCTION_CANCEL_TITLE = "拍卖取消"
AUCTION_CANCEL_CONTENT = "您拍卖的{0}已经流拍了。拍品已经放入您的附件当中，请注意查收"

TIMERD_CALLBACK_AUCTION = "/api/timerd/auction/"

AUCTION_LOCK_KEY = "lock_auction_{0}"
AUCTION_LOCK_TIME = 2

class AuctionItem(object):
    def __init__(self):
        self.id = ""
        self.server_id = 0
        self.char_id = 0
        self.club_name = ""

        self.staff_id = 0
        self.exp = 0
        self.level = 0
        self.status = 0
        self.skills = {}

        self.quality = 0
        self.jingong = 0
        self.qianzhi = 0
        self.xintai = 0
        self.baobing = 0
        self.fangshou = 0
        self.yunying = 0
        self.yishi = 0
        self.caozuo = 0
        self.zhimingdu = 0

        self.start_at = 0
        self.tp = 0
        self.min_price = 0
        self.max_price = 0

        self.bidder = 0
        self.bidding = 0
        self.key = ""

    @classmethod
    def create_from_staff_object(cls, staff, tp, min_price, max_price):
        """

        :type staff: core.staff.Staff
        """
        obj = cls()

        obj.id = make_string_id()
        obj.server_id = staff.server_id
        obj.char_id = staff.char_id
        obj.club_name = Club(staff.server_id, staff.char_id, load_staff=False).name

        obj.staff_id = staff.id
        obj.exp = staff.exp
        obj.level = staff.level
        obj.status = staff.status
        obj.skills = {str(k): v for k, v in staff.skills.iteritems()}

        obj.quality = staff.quality
        obj.jingong = staff.jingong
        obj.qianzhi = staff.qianzhi
        obj.xintai = staff.xintai
        obj.baobing = staff.baobing
        obj.fangshou = staff.fangshou
        obj.yunying = staff.yunying
        obj.yishi = staff.yishi
        obj.caozuo = staff.caozuo
        obj.zhimingdu = staff.zhimingdu

        obj.start_at = arrow.utcnow().timestamp
        obj.tp = tp
        obj.min_price = min_price
        obj.max_price = max_price

        return obj

    @classmethod
    def load_from_data(cls, server_id, data):
        obj = cls()
        obj.id = data['_id']
        obj.server_id = server_id
        obj.char_id = data['char_id']
        obj.club_name = data['club_name']

        obj.staff_id = data['staff_id']
        obj.exp = data['exp']
        obj.level = data['level']
        obj.status = data['status']
        obj.skills = data['skills']

        obj.quality = data['quality']
        obj.jingong = data['jingong']
        obj.qianzhi = data['qianzhi']
        obj.xintai = data['xintai']
        obj.baobing = data['baobing']
        obj.fangshou = data['fangshou']
        obj.yunying = data['yunying']
        obj.yishi = data['yishi']
        obj.caozuo = data['caozuo']
        obj.zhimingdu = data['zhimingdu']

        obj.start_at = data['start_at']
        obj.tp = data['tp']
        obj.min_price = data['min_price']
        obj.max_price = data['max_price']

        obj.bidder = data['bidder']
        obj.bidding = data['bidding']
        obj.key = data['key']

        return obj

    @property
    def end_at(self):
        return self.start_at + AUCTION_TYPE_HOURS[self.tp] * 3600

    def to_document(self):
        doc = MongoAuctionStaff.document()
        doc['_id'] = self.id
        doc['char_id'] = self.char_id
        doc['club_name'] = self.club_name
        doc['staff_id'] = self.staff_id
        doc['exp'] = self.exp
        doc['level'] = self.level
        doc['status'] = self.status
        doc['skills'] = self.skills
        doc['quality'] = self.quality
        doc['jingong'] = self.jingong
        doc['qianzhi'] = self.qianzhi
        doc['xintai'] = self.xintai
        doc['baobing'] = self.baobing
        doc['fangshou'] = self.fangshou
        doc['yunying'] = self.yunying
        doc['yishi'] = self.yishi
        doc['caozuo'] = self.caozuo
        doc['yishi'] = self.yishi
        doc['caozuo'] = self.caozuo
        doc['zhimingdu'] = self.zhimingdu

        doc['start_at'] = self.start_at
        doc['tp'] = self.tp
        doc['min_price'] = self.min_price
        doc['max_price'] = self.max_price

        doc['bidder'] = self.bidder
        doc['bidding'] = self.bidding
        doc['key'] = self.key

        return doc

    def make_proto_msg(self):
        msg = MsgAuctionItem()
        msg.item_id = self.id
        msg.club_name = self.club_name
        msg.staff_id = self.staff_id

        msg.start_time = self.start_at
        msg.end_at = self.end_at
        msg.min_price = self.min_price
        msg.max_price = self.max_price
        msg.bidding = self.bidding

        return msg

    def finish(self):
        if self.bidder:
            self._success()
        else:
            self._fail()

    def _success(self):
        staff_name = ConfigStaff.get(self.staff_id).name

        StaffManger(self.server_id, self.bidder).add_staff(self.staff_id, self.exp, self.level, self.status,
                                                           self.skills)
        # 通知客户端从竞价列表中移除物品
        AuctionManager(self.server_id, self.bidder).send_bidding_remove_notify(self.id)
        # 通知竞标获胜者获胜邮件
        MailManager(self.server_id, self.char_id).add(
            AUCTION_BIDDING_SUCCESS_TITLE,
            AUCTION_BIDDING_SUCCESS_CONTENT.format(staff_name),
            "",
        )

        MongoAuctionStaff.db(self.server_id).delete_one({'_id': self.id})
        # 返还竞拍失败者金币, 并从竞价列表移除
        docs = MongoBidding.db(self.server_id).find({'items': self.id})
        for doc in docs:
            char_id = doc['_id']
            if char_id == self.bidder:
                continue

            gold = doc['item_{0}'.format(self.id)]
            drop = Drop()
            drop.gold = gold
            attachment = drop.to_json()

            MailManager(self.server_id, char_id).add(
                AUCTION_BIDDING_FAIL_TITLE,
                AUCTION_BIDDING_FAIL_CONTENT.format(staff_name),
                attachment
            )

            AuctionManager(self.server_id, char_id).send_bidding_remove_notify(self.id)

        # 删除竞价者列表该物品数据
        MongoBidding.db(self.server_id).update_one(
            {'_id': self.char_id},
            {
                '$pull': {'items': self.id},
                '$unset': {'item_{0}'.format(self.id): 1}
            }
        )

        # 发送邮件给拍卖者
        seller_drop = Drop()
        seller_drop.gold = math.floor(int(self.bidding * AUCTION_TYPE_TAX[self.tp]))
        attachment_seller = seller_drop.to_json()

        MailManager(self.server_id, self.char_id).add(
            AUCTION_SUCCESS_TITLE,
            AUCTION_SUCCESS_CONTENT.format(staff_name, seller_drop.gold),
            attachment_seller,
        )

    def _fail(self):
        StaffManger(self.server_id, self.char_id).add_staff(self.staff_id, self.exp, self.level, self.status,
                                                            self.skills)
        staff_name = ConfigStaff.get(self.staff_id).name
        MailManager(self.server_id, self.char_id).add(
            AUCTION_FAIL_TITLE,
            AUCTION_FAIL_CONTENT.format(staff_name),
        )


class AuctionManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoBidding.exist(self.server_id, self.char_id):
            doc = MongoBidding.document()
            doc['_id'] = self.char_id
            MongoBidding.db(self.server_id).insert_one(doc)

    def search(self):
        # TODO: condition query
        docs = MongoAuctionStaff.db(self.server_id).find()
        return [AuctionItem.load_from_data(self.server_id, doc) for doc in docs]

    def sell(self, staff_id, tp, min_price, max_price):
        staff = StaffManger(self.server_id, self.char_id).get_staff(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        if TrainingShop(self.server_id, self.char_id).staff_is_training(staff_id) or \
                TrainingProperty(self.server_id, self.char_id).staff_is_training(staff_id) or \
                TrainingExp(self.server_id, self.char_id).staff_is_training(staff_id) or \
                TrainingBroadcast(self.server_id, self.char_id).staff_is_training(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("AUCTION_STAFF_IS_BUSY"))

        if tp not in AUCTION_TYPE_HOURS:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if min_price > max_price:
            raise GameException(ConfigErrorMessage.get_error_id("AUCTION_MIN_LARGE_THAN_MAX"))

        item = AuctionItem.create_from_staff_object(staff, tp, min_price, max_price)
        data = {
            'sid': self.server_id,
            'cid': self.char_id,
            'item_id': item.id,
        }

        end_at = item.end_at
        item.key = Timerd.register(end_at, TIMERD_CALLBACK_AUCTION, data)

        # 写入数据库
        MongoAuctionStaff.db(self.server_id).insert_one(item.to_document())

        # 同步拍卖数据
        self.send_sell_list_notify([item.id])

    def cancel(self, item_id):
        try:
            with Lock(self.server_id).lock(AUCTION_LOCK_TIME, AUCTION_LOCK_KEY.format(item_id)):
                doc = MongoAuctionStaff.db(self.server_id).find_one({'_id': item_id})
                if not doc:
                    raise GameException(ConfigErrorMessage.get_error_id("AUCTION_ITEM_NOT_EXIST"))

                item = AuctionItem.load_from_data(self.server_id, doc)

                if item.char_id != self.char_id:
                    raise GameException(ConfigErrorMessage.get_error_id("AUCTION_NOT_THE_OWNER"))

                if item.bidder:
                    raise GameException(ConfigErrorMessage.get_error_id("AUCTION_BIDDING_NOW"))

                # 删除拍卖物品数据
                MongoAuctionStaff.db(self.server_id).delete_one({'_id': item_id})
                # 取消定时任务
                Timerd.cancel(item.key)
                # 邮件通知, 返还staff
                StaffManger(self.server_id, self.char_id).add_staff(item.id, item.exp, item.level, item.status, item.skills)
                staff_name = ConfigStaff.get(doc['staff_id']).name
                MailManager(self.server_id, self.char_id).add(
                    AUCTION_CANCEL_TITLE,
                    AUCTION_CANCEL_CONTENT.format(staff_name),
                )
                # 通知客户端从出售列表移除
                self.send_sell_remove_notify(item_id)
        except LockTimeOut:
            GameException(ConfigErrorMessage.get_error_id("AUCTION_ITEM_OPERATING"))

    def bidding(self, item_id, price):
        lock_key = item_id
        try:
            with Lock(self.server_id).lock(2, lock_key):
                sale = False
                doc = MongoAuctionStaff.db(self.server_id).find_one({'_id': item_id})
                if not doc:
                    raise GameException(ConfigErrorMessage.get_error_id("AUCTION_ITEM_NOT_EXIST"))

                item = AuctionItem.load_from_data(self.server_id, doc)

                if StaffManger(self.server_id, self.char_id).has_staff(item.staff_id):
                    raise GameException(ConfigErrorMessage.get_error_id("AUCTION_STAFF_ALREADY_HAVE"))

                if price < item.min_price:
                    raise GameException(ConfigErrorMessage.get_error_id("AUCTION_BIDDING_TOO_LOW"))

                if item.bidding >= price:
                    raise GameException(ConfigErrorMessage.get_error_id("AUCTION_BIDDING_LOW_THAN_CURRENT"))

                if price >= item.max_price:
                    price = item.max_price
                    sale = True

                bidding_doc = MongoBidding.db(self.server_id).find_one({'_id': self.char_id})
                key = 'item_{0}'.format(item_id)
                history_bid = bidding_doc.get(key, 0)

                need_gold = price - history_bid
                if need_gold <= 0:
                    raise GameException(ConfigErrorMessage.get_error_id("AUCTION_BIDDING_MUST_GREATER_THAN_HISTORY"))

                message = u"Auction Bidding {0} price {1}".format(item_id, need_gold)
                with Resource(self.server_id, self.char_id).check(gold=-need_gold, message=message):
                    if sale:
                        # 竞标结束
                        item.finish()
                        # 取消定时任务
                        Timerd.cancel(item.key)
                    else:
                        # 更新物品竞拍信息
                        MongoAuctionStaff.db(self.server_id).update_one(
                            {'_id': doc['_id']},
                            {'$set': {'bidding': price, 'bidder': self.char_id}}
                        )
                        # 更新竞拍者列表信息
                        MongoBidding.db(self.server_id).update_one(
                            {'_id': item_id},
                            {
                                {'$addToSet': {'items': item_id}},
                                {'$set': {key: price}}
                            }
                        )

                        # 通知竞拍失败者 最新竞拍信息
                        bidder_docs = MongoBidding.db(self.server_id).find({'items': item.id})
                        for bidder in bidder_docs:
                            if bidder['_id'] != self.char_id:
                                AuctionManager(self.server_id, bidder['_id']).send_bidding_list_notify([item.id])

        except LockTimeOut:
            raise GameException(ConfigErrorMessage.get_error_id("AUCTION_ITEM_OPERATING"))

    # 定时回调, 拍卖时间结束, 处理拍卖物品
    def callback(self, item_id):
        try:
            with Lock(self.server_id).lock(2, item_id):
                doc = MongoAuctionStaff.db(self.server_id).find_one({'_id': item_id})
                if not doc:
                    return

                item = AuctionItem.load_from_data(self.server_id, doc)
                item.finish()
        except LockTimeOut:
            raise GameException(ConfigErrorMessage.get_error_id("AUCTION_ITEM_OPERATING"))

    def send_sell_list_notify(self, item_ids=None):
        if not item_ids:
            act = ACT_INIT
            condition = {'char_id': self.char_id}
        else:
            act = ACT_UPDATE
            condition = {'_id': {'$in': item_ids}}

        docs = MongoAuctionStaff.db(self.server_id).find(condition)

        notify = StaffAuctionSellListNotify()
        notify.act = act
        for doc in docs:
            notify_item = notify.items.add()
            item = AuctionItem.load_from_data(self.server_id, doc)
            notify_item.MergeFrom(item.make_proto_msg())

        MessagePipe(self.char_id).put(msg=notify)

    def send_sell_remove_notify(self, item_id):
        notify = StaffAuctionSellRemoveNotify()
        notify.item_id = item_id
        MessagePipe(self.char_id).put(msg=notify)

    def send_bidding_list_notify(self, item_ids=None):
        doc = MongoBidding.db(self.server_id).find_one({'_id': self.char_id})

        if item_ids:
            act = ACT_UPDATE
        else:
            act = ACT_INIT
            item_ids = doc['items']

        item_docs = MongoAuctionStaff.db(self.server_id).find({'_id': {'$in': item_ids}})
        items = {d['_id']: d for d in item_docs}

        notify = StaffAuctionBidingListNotify()
        notify.act = act

        for _id in item_ids:
            item_obj = AuctionItem.load_from_data(self.server_id, items[_id])

            notify_item = notify.items.add()
            notify_item.item.MergeFrom(item_obj.make_proto_msg())
            notify_item.item.my_bid = doc['item_{0}'.format(_id)]

            MessagePipe(self.char_id).put(msg=notify)

    def send_bidding_remove_notify(self, item_id):
        notify = StaffAuctionBidingRemoveNotify()
        notify.item_id = item_id
        MessagePipe(self.char_id).put(msg=notify)
