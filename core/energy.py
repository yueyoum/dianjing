# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       energy
Date Created:   2016-06-02 10-16
Description:

"""

import arrow

from dianjing.exception import GameException

from core.mongo import MongoEnergy
from core.value_log import ValueLogEnergyBuyTimes
from core.vip import VIP
from core.resource import ResourceClassification, money_text_to_item_id

from config import ConfigErrorMessage, ConfigEnergyBuyCost

from utils.message import MessagePipe

from protomsg.energy_pb2 import EnergyNotify

MAX_ENERGY_SOFT_LIMIT = 120
MAX_ENERGY_HARD_LIMIT = 999
RECOVER_INTERVAL = 60 * 5


class BuyTimeInfo(object):
    __slots__ = ['buy_times', 'remained_buy_times', 'buy_cost']

    def __init__(self, server_id, char_id):
        self.buy_times = ValueLogEnergyBuyTimes(server_id, char_id).count_of_today()
        self.remained_buy_times = VIP(server_id, char_id).energy_buy_times - self.buy_times
        if self.remained_buy_times < 0:
            self.remained_buy_times = 0

        self.buy_cost = ConfigEnergyBuyCost.get_cost(self.buy_times + 1)


class Energy(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.doc = MongoEnergy.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoEnergy.document()
            self.doc['_id'] = self.char_id
            self.doc['current'] = MAX_ENERGY_SOFT_LIMIT
            self.doc['last_add_at'] = arrow.utcnow().timestamp

            MongoEnergy.db(self.server_id).insert_one(self.doc)

        self.recover()

    def recover(self):
        # 自己按照时间恢复
        # 并不是按照时间间隔来调用的， 而是调用时再判断恢复了多少

        if self.doc['current'] >= MAX_ENERGY_SOFT_LIMIT:
            return

        now = arrow.utcnow().timestamp
        passed_seconds = now - self.doc['last_add_at']
        times = passed_seconds / RECOVER_INTERVAL
        if times < 0:
            return

        can_add_times = MAX_ENERGY_SOFT_LIMIT - self.doc['current']
        if can_add_times < times:
            times = can_add_times

        self.doc['current'] += times
        # NOTE, 这里直接加到当前时间
        self.doc['last_add_at'] = now

        MongoEnergy.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'current': self.doc['current'],
                'last_add_at': self.doc['last_add_at'],
            }}
        )

    @property
    def energy(self):
        return self.doc['current']

    @property
    def next_recover_timestamp(self):
        if self.doc['current'] >= MAX_ENERGY_SOFT_LIMIT:
            return 0

        return self.doc['last_add_at'] + RECOVER_INTERVAL

    def is_full(self):
        return self.doc['current'] >= MAX_ENERGY_SOFT_LIMIT

    def check(self, value):
        new_value = self.doc['current'] - value
        if new_value < 0:
            raise GameException(ConfigErrorMessage.get_error_id("ENERGY_NOT_ENOUGH"))

        return new_value

    def remove(self, value):
        new_value = self.check(value)

        self.doc['current'] = new_value
        MongoEnergy.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'current': new_value
            }}
        )

        self.send_notify()

    def add(self, value):
        # 外部来增加体力
        self.doc['current'] += value
        if self.doc['current'] > MAX_ENERGY_HARD_LIMIT:
            self.doc['current'] = MAX_ENERGY_HARD_LIMIT

        MongoEnergy.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'current': self.doc['current']
            }}
        )

        self.send_notify()

    def buy(self):
        # 购买体力
        ri = BuyTimeInfo(self.server_id, self.char_id)
        if not ri.remained_buy_times:
            raise GameException(ConfigErrorMessage.get_error_id("ENERGY_CANNOT_BUY_NO_TIMES"))

        if self.doc['current'] + 60 > MAX_ENERGY_HARD_LIMIT:
            raise GameException(ConfigErrorMessage.get_error_id("ENERGY_CANNOT_BUY_REACH_HARD_LIMIT"))

        cost = [(money_text_to_item_id('diamond'), ri.buy_cost), ]
        rc = ResourceClassification.classify(cost)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id, message="Energy.buy")

        ValueLogEnergyBuyTimes(self.server_id, self.char_id).record()
        self.add(60)

    def send_notify(self):
        ri = BuyTimeInfo(self.server_id, self.char_id)

        notify = EnergyNotify()
        notify.current_energy = self.doc['current']
        notify.max_energy = MAX_ENERGY_SOFT_LIMIT
        notify.remained_buy_times = ri.remained_buy_times
        notify.buy_cost = ri.buy_cost
        notify.recover_interval = RECOVER_INTERVAL
        notify.next_recover_timestamp = self.next_recover_timestamp

        MessagePipe(self.char_id).put(msg=notify)
