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
from core.mongo import MongoStaffAuction, MongoStaff, MongoBidding
from core.club import Club
from core.resource import Resource
from core.mail import MailManager
from core.package import Drop

from utils.api import Timerd
from utils.functional import make_string_id

from config import ConfigErrorMessage, ConfigStaffStatus

from protomsg.auction_pb2 import (
    StaffAuctionNotify,
    StaffAuctionUserNotify,
    StaffAuctionUserItemRemoveNotify,
    StaffAuctionListNotify,
    AuctionStaffItem,
    StaffAuctionRemoveNotify,
    hours_8,
    hours_16,
    hours_24,
)
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE

from utils.message import MessagePipe


AUCTION_TYPE_TIME = {
    str(hours_8): 8,
    str(hours_16): 16,
    str(hours_24): 24,
}

AUCTION_BIDDING_FAIL_TITLE = "竞标成功"
AUCTION_BIDDING_FAIL_CONTENT = "您成功竞拍到{0}，已经放入您的附件当中，请注意查收。"

AUCTION_BIDDING_SUCCESS_TITLE = "竞标成功"
AUCTION_BIDDING_SUCCESS_CONTENT = "您成功竞拍到{0}，已经放入您的附件当中，请注意查收。"

AUCTION_SUCCESS_TITLE = "拍卖成功"
AUCTION_SUCCESS_CONTENT = "您拍卖的{0}已经成功拍出，扣除税金后，总共获得{1}软妹币，已经放入您的附件当中，请注意查收"

AUCTION_FAIL_TITLE = "拍卖失败"
AUCTION_FAIL_CONTENT = "您拍卖的{0}超过拍卖时限而无人竞拍，已经流拍了。流拍的拍品已经放入您的附件当中，请注意查收"

AUCTION_CANCEL_TITLE = "拍卖取消"
AUCTION_CANCEL_CONTENT = "您拍卖的{0}超过拍卖时限而无人竞拍，已经流拍了。流拍的拍品已经放入您的附件当中，请注意查收"

TIMERD_CALLBACK_AUCTION = "/api/timerd/auction/"


def get_tax_rate_by_tp(tp):
    if tp == hours_8:
        return 0.75
    elif tp == hours_16:
        return 0.73
    else:
        return 0.7


class AuctionItem(object):

    def __init__(self, data):
        # TODO: uuid
        self.id = data.get('_id', "")
        self.char_id = data.get('char_id', 0)
        self.club_name = data.get('club_name', 0)
        # 员工属性
        self.staff_id = data.get('staff_id', 0)
        self.level = data.get('level', 1)
        self.exp = data.get('exp', 0)
        self.status = data.get('status', ConfigStaffStatus.DEFAULT_STATUS)
        self.jingong = data.get('jingong', 0)
        self.qianzhi = data.get('qianzhi', 0)
        self.xintai = data.get('xintai', 0)
        self.fangshou = data.get('fangshou', 0)
        self.yunying = data.get('yunying', 0)
        self.yishi = data.get('yishi', 0)
        self.caozuo = data.get('caozuo', 0)
        self.zhimingdu = data.get('zhimingdu', 0)

        skills = data.get('skills', {})
        self.skills = {int(k): v['level'] for k, v in skills.iteritems()}
        # 拍卖设置
        self.start_time = arrow.utcnow().timestamp
        self.tp = data.get('tp', 0)
        self.end_at = self.start_time + AUCTION_TYPE_TIME[str(self.tp)] * 60 * 60
        self.min_price = data.get('min_price', 0)
        self.max_price = data.get('max_price', 0)
        # 拍卖情况
        self.bidder = data.get('bidder', 0)
        self.bidding = data.get('bidding', 0)

    def make_proto_msg(self):
        from protomsg.auction_pb2 import AuctionItem
        msg = AuctionItem()
        msg.item_id = self.id
        msg.club_name = self.club_name
        msg.staff_id = self.staff_id

        msg.start_time = self.start_time
        msg.end_at = self.end_at
        msg.min_price = self.min_price
        msg.max_price = self.max_price
        msg.bidding = self.bidding

        return msg


class AuctionManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def search(self):
        self.send_common_auction_notify()

    def sell(self, staff_id, tp, min_price, max_price):
        """
         出售员工
            1 是否拥有该员工
            2 出售时长时是否是规定类型
            3 最低价是否高于最高价
            4 员工是否空闲
            5 获取员工属性
            6 将员工从玩家员工列表中移除
            7 写入到服务器出售列表
            8 同步数据到客户端
        """
        if not StaffManger(self.server_id, self.char_id).has_staff(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        if tp not in [hours_8, hours_16, hours_24]:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if min_price > max_price:
            raise GameException(ConfigErrorMessage.get_error_id("AUCTION_MIN_LARGE_THAN_MAX"))

        # 获取员工数值
        doc_staff = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, {'staff.{0}'.format(staff_id): 1})
        staff = doc_staff.get('staff.{0}'.format(staff_id), {})
        # 移除员工
        StaffManger(self.server_id, self.char_id).remove(staff_id)

        insert_doc = MongoStaffAuction.document()
        insert_doc['_id'] = make_string_id()
        insert_doc['char_id'] = self.char_id
        insert_doc['club_name'] = Club(self.server_id, self.char_id).name
        # 员工属性
        insert_doc['staff_id'] = staff_id
        insert_doc['level'] = staff.get('level', 1)
        insert_doc['exp'] = staff.get('exp', 0)
        insert_doc['status'] = staff.get('status', ConfigStaffStatus.DEFAULT_STATUS)
        insert_doc['jingong'] = staff.get('jingong', 0)
        insert_doc['qianzhi'] = staff.get('qianzhi', 0)
        insert_doc['xintai'] = staff.get('xintai', 0)
        insert_doc['fangshou'] = staff.get('fangshou', 0)
        insert_doc['yunying'] = staff.get('yunying', 0)
        insert_doc['yishi'] = staff.get('yishi', 0)
        insert_doc['caozuo'] = staff.get('caozuo', 0)
        insert_doc['zhimingdu'] = staff.get('zhimingdu', 0)

        skills = staff.get('skills', {})
        insert_doc['skills'] = {int(k): v['level'] for k, v in skills.iteritems()}
        # 拍卖设置
        insert_doc['start_at'] = arrow.utcnow().timestamp
        insert_doc['tp'] = tp
        insert_doc['min_price'] = min_price
        insert_doc['max_price'] = max_price
        # 拍卖情况
        insert_doc['bidder'] = 0
        insert_doc['bidding'] = 0

        # 设置定时器
        data = {
                'sid': self.server_id,
                'cid': self.char_id,
                'item_id': insert_doc['_id']
            }
        end_at = insert_doc['start_at'] + AUCTION_TYPE_TIME[str(tp)] * 60 * 60
        key = Timerd.register(end_at, TIMERD_CALLBACK_AUCTION, data)
        insert_doc['key'] = key

        # 写入数据库
        MongoStaffAuction.db(self.server_id).insert_one(insert_doc)

        # 同步数据
        self.send_user_auction_notify([insert_doc['_id']])

    def cancel(self, item_id):
        """
        取消拍卖
            1 是否有这个商品
            2 是否是商品拥有者
            3 删除商品, 并发还给玩家

            :type item_id : str
        """
        doc = MongoStaffAuction.db(self.server_id).find_one({'_id': item_id})
        if not doc:
            raise GameException(ConfigErrorMessage.get_error_id("AUCTION_ITEM_NOT_EXIST"))

        if doc['char_id'] != self.char_id:
            raise GameException(ConfigErrorMessage.get_error_id("AUCTION_NOT_THE_OWNER"))

        if doc['bidding']:
            raise GameException(ConfigErrorMessage.get_error_id("AUCTION_BIDDING_NOW"))

        # 删除拍卖物品数据
        MongoStaffAuction.db(self.server_id).delete_one({'_id': item_id})
        # 取消定时任务
        Timerd.cancel(doc['key'])
        # 玩家staff同步
        StaffManger(self.server_id, self.char_id).add_staff(doc)

        MailManager(self.server_id, self.char_id).add(
            AUCTION_CANCEL_TITLE,
            AUCTION_CANCEL_CONTENT,
            "",
        )

        notify = StaffAuctionUserItemRemoveNotify()
        notify.id.append(item_id)
        MessagePipe(self.char_id).put(msg=notify)

    def bidding(self, item_id, price):
        """
        竞标
            1 商品是否还存在
            2 竞标价是否低于最低价
            3 竞标价是否高于当前竞标价
            4 竞标价是否高于一口价
            5 玩家是否有足够资源
            6 竞拍成功处理
                1 一口价处理
                2 普通竞标处理
            7 竞标失败者处理

            :type item_id : str
            :type price : int
        """
        sale = False
        doc = MongoStaffAuction.db(self.server_id).find_one({'_id': item_id})
        if not doc:
            raise GameException(ConfigErrorMessage.get_error_id("AUCTION_ITEM_NOT_EXIST"))

        if StaffManger(self.server_id, self.char_id).has_staff(doc['staff_id']):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        # 如果竞标过该物品
        bidding_doc = MongoBidding.db(self.server_id).find_one({'_id': item_id})
        if bidding_doc and self.char_id in bidding_doc['bidders']:
            history_bid = bidding_doc.get('{0}-{1}'.format(item_id, self.char_id), 0)
        else:
            history_bid = 0

        price += history_bid
        if price < doc['min_price']:
            raise GameException(ConfigErrorMessage.get_error_id("AUCTION_BIDDING_TOO_LOW"))

        if doc['bidding'] >= price:
            raise GameException(ConfigErrorMessage.get_error_id("AUCTION_BIDDING_LOW_THAN_CURRENT"))

        if price > doc['max_price']:
            price = doc['max_price']
            sale = True

        need_gold = price - history_bid
        # 资源检测
        message = u"Bidding Auction {0} price {1}".format(item_id, need_gold)
        with Resource(self.server_id, self.char_id).check(gild=-need_gold, message=message):
            if sale:
                self.finish(self.server_id, self.char_id, item_id, doc, price)

            else:
                # 更新物品竞拍信息
                MongoStaffAuction.db(self.server_id).update_one(
                    {'_id': doc['_id']},
                    {'$set': {'bidding': price, 'bidder': self.char_id}}
                )
                # 更新竞拍者列表信息
                MongoBidding.db(self.server_id).update_one(
                    {'_id': item_id},
                    {'$pull': {'bidding': self.char_id},
                     '$set': {'{0}-{1}'.format(item_id, self.char_id): price}
                     },
                    upsert=True,
                )

                # 通知竞拍失败者 最新竞拍信息
                bidder_doc = MongoBidding.db(self.server_id).find_one({'_id': item_id}, {'bidders': 1})
                for char_id in bidder_doc.get('bidder', []):
                    AuctionManager(self.server_id, char_id).send_bidding_notify([item_id])

    # 定时回调, 拍卖时间结束, 处理拍卖物品
    def callback(self, item_id):
        """
        拍卖时间结束处理
            1 是否有竞标, bidding > 0
            2 有, 则竞标者获胜, 添加到玩家身上
            3 无, 发还给玩家

            :type item_id : str
        """
        doc = MongoStaffAuction.db(self.server_id).find_one({'_id': item_id})
        if doc:
            if doc['bidding'] > 0:
                self.finish(self.server_id, doc['bidder'], item_id, doc, doc['bidding'])
            else:
                StaffManger(self.server_id, self.char_id).add_staff(doc)

                MailManager(self.server_id, self.char_id).add(
                    AUCTION_FAIL_TITLE,
                    AUCTION_FAIL_CONTENT,
                    "",
                )

    # 拍卖完成处理
    def finish(self, server_id, char_id, item_id, doc, price):
        """
            char_id  获胜者ID
        """
        StaffManger(server_id, char_id).add_staff(doc)
        MongoStaffAuction.db(server_id).delete_one({'_id': item_id})
        # 返还竞拍失败还者金币, 并从竞价列表移除
        bidder_doc = MongoBidding.db(server_id).find_one({'_id': item_id}, {'bidders': 1})
        for bidder_id in bidder_doc.get('bidder', []):
            if bidder_id != char_id:
                # 通过邮箱返还金币
                drop = Drop()
                drop.gold = bidder_doc.get('{0}-{1}'.format(item_id, char_id), 0)
                attachment = drop.to_json()

                MailManager(bidder_id, bidder_id).add(
                    AUCTION_BIDDING_FAIL_TITLE,
                    AUCTION_BIDDING_FAIL_CONTENT,
                    attachment,
                )
                # 通知客户端从移除竞价列表中移除物品
                notify = StaffAuctionRemoveNotify()
                notify.item_id = item_id
                MessagePipe(bidder_id).put(msg=notify)

            # 删除竞价者列表该物品数据
            MongoBidding.db(server_id).delete_one({'_id': item_id})
            # 发送邮件给拍卖者
            seller_drop = Drop()
            seller_drop.gold = math.floor(price * get_tax_rate_by_tp(doc['tp']))
            attachment_seller = seller_drop.to_json()

            MailManager(server_id, doc['char_id']).add(
                AUCTION_SUCCESS_TITLE,
                AUCTION_SUCCESS_CONTENT,
                attachment_seller,
            )

    def get_bid_list(self):
        self.send_bidding_notify()

    def send_common_auction_notify(self, item_ids=None):
        """
        通知用户员工转会窗口信息
            1 如果 item_ids 非空, 获取 item_ids 中转会信息
                否则, 获取所有转会信息
            2 组装信息
        """
        if item_ids:
            projection = {'_id': {'$in': {item_ids}}}
        else:
            projection = {}

        notify = StaffAuctionNotify()
        notify.act = ACT_INIT
        for doc in MongoStaffAuction.db(self.server_id).find(projection):
            notify_item = notify.items.add()
            item = AuctionItem(doc)
            notify_item.MergeFrom(item.make_proto_msg())

        MessagePipe(self.char_id).put(msg=notify)

    def send_user_auction_notify(self, item_ids=None):
        """
        通知用户拍卖
            1 如果 item_ids 为空, 初始化, 通知所有信息;
                否则, 只通知 item_ids 中信息
            2 组装发送信息
        """
        if not item_ids:
            act = ACT_INIT
            projection = {'char_id': self.char_id}
        else:
            act = ACT_UPDATE
            projection = {'_id': {'$in': item_ids}}

        doc = MongoStaffAuction.db(self.server_id).find(projection)

        notify = StaffAuctionUserNotify()
        notify.act = act
        for staff in doc:
            notify_item = notify.items.add()
            item = AuctionItem(staff)
            notify_item.MergeFrom(item.make_proto_msg())

        MessagePipe(self.char_id).put(msg=notify)

    def send_bidding_notify(self, item_ids=None):
        """
        通知玩家竞拍信息
        """
        if item_ids:
            act = ACT_UPDATE
            projection = {'_id': {'$in': item_ids}}
        else:
            act = ACT_INIT
            projection = {'bidders': self.char_id}

        bid_doc = MongoBidding.db(self.server_id).find(projection)
        if bid_doc:
            item_ids = [doc['_id'] for doc in bid_doc]

            auction_doc = MongoStaffAuction.db(self.server_id).find({'_id': {'$in': item_ids}})
            notify = StaffAuctionListNotify()
            notify.act = act
            for auction_item in auction_doc:
                notify_item = notify.items.add()
                item = AuctionItem(auction_item)

                msg = AuctionStaffItem()
                msg.items = item.make_proto_msg()
                msg.my_bid = bid_doc[item.id]

                notify_item.MergeFrom(msg)

            MessagePipe(self.char_id).put(msg=notify)

