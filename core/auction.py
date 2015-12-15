# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       auction
Date Created:   2015-12-15 09:36
Description:    拍卖系统  电竞经理/员工系统/拍卖行

"""
import arrow

from dianjing.exception import GameException

from core.staff import StaffManger
from core.mongo import MongoStaffAuction, MongoStaff

from config import ConfigErrorMessage, ConfigStaffStatus


class AuctionItem(object):
    def __init__(self, doc):
        self.char_id = doc['char_id']
        self.staff_id = doc['staff_id']
        self.level = doc['level']
        self.cur_exp = doc['cur_exp']
        self.max_exp = doc['max_exp']
        self.status = doc['status']
        self.jingong = doc['jingong']
        self.qianzhi = doc['qianzhi']
        self.xintai = doc['xintai']
        self.fangshou = doc['fangshou']
        self.yunying = doc['yunying']
        self.yishi = doc['yishi']
        self.caozuo = doc['caozuo']
        self.zhimingdu = doc['zhimingdu']
        self.start_time = doc['start_time']
        self.tp = doc['tp']
        self.auction_inc = doc['auction_inc']
        self.min_price = doc['min_price']
        self.max_price = doc['max_price']


class AuctionManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def search(self):
        pass

    def sell(self, staff_id, tp, min_price, max_price):
        """
         出售员工
            1 是否拥有该员工
            2 出售时长时是否是规定类型
            3 最低价是否高于最高价
            4 检查员工是否空闲
            4 获取玩家员工属性
            5 将原共从玩家员工列表中移除, 并加到出售列表
            6 加入到服务器出售列表
        """
        if not StaffManger(self.server_id, self.char_id).has_staff(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        if tp not in [1, 2, 3]:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if min_price > max_price:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        doc_staff = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, {'staff.{0}'.format(staff_id): 1})
        staff = doc_staff.get('staff.{0}'.format(staff_id), {})

        doc = MongoStaffAuction.document()
        doc['char_id'] = self.char_id
        doc['staff_id'] = staff_id
        doc['level'] = staff.get('level', 1)
        doc['exp'] = staff.get('exp', 0)
        doc['status'] = staff.get('status', ConfigStaffStatus.DEFAULT_STATUS)
        doc['jingong'] = staff.get('jingong', 0)
        doc['qianzhi'] = staff.get('qianzhi', 0)
        doc['xintai'] = staff.get('xintai', 0)
        doc['fangshou'] = staff.get('fangshou', 0)
        doc['yunying'] = staff.get('yunying', 0)
        doc['yishi'] = staff.get('yishi', 0)
        doc['caozuo'] = staff.get('caozuo', 0)
        doc['zhimingdu'] = staff.get('zhimingdu', 0)

        skills = staff.get('skills', {})
        doc['skills'] = {int(k): v['level'] for k, v in skills.iteritems()}

        doc['start_time'] = arrow.utcnow().timestamp
        doc['tp'] = tp
        doc['auction_inc'] = 0
        doc['min_price'] = min_price
        doc['max_price'] = max_price

    def cancel(self, item_id):
        pass

    def bidding(self, auction_item_id, price):
        pass

    def send_common_auction_notify(self):
        pass

    def send_user_auction_notify(self):
        pass

