# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       party
Date Created:   2016-09-19 13:36
Description:

"""
import random

from dianjing.exception import GameException

from core.mongo import MongoParty
from core.club import Club
from core.union import Union
from core.resource import ResourceClassification, money_text_to_item_id
from core.mail import MailManager
from core.value_log import ValueLogPartyCreateTimes, ValueLogPartyJoinTimes, ValueLogPartyEngageTimes

from utils.message import MessagePipe
from utils.functional import get_start_time_of_today
from utils.operation_log import OperationLog

from config import GlobalConfig, ConfigErrorMessage, ConfigPartyLevel, ConfigPartyBuyItem, ConfigItemNew

from protomsg.party_pb2 import PartyNotify

from api import api_handle

# 这部分功能都是 socket 发来的调用

MAX_CREATE_TIMES = 100
MAX_JOIN_TIMES = 100


def get_party_open_time_range(h1, h2):
    today = get_start_time_of_today()

    time1 = today.replace(hours=h1)
    time2 = today.replace(hours=h2)

    return time1, time2


def get_time_of_tomorrow(h):
    today = get_start_time_of_today()
    today = today.replace(days=1)
    today = today.replace(hour=h)
    return today


class Party(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.doc = MongoParty.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoParty.document()
            self.doc['_id'] = self.char_id
            MongoParty.db(self.server_id).insert_one(self.doc)

    @classmethod
    def clean_talent_id(cls, server_id):
        char_ids = OperationLog.get_recent_action_char_ids(server_id)

        condition = {'$and': [
            {'_id': {'$in': char_ids}},
            {'talent_id': {'$gt': 0}}
        ]}

        docs = MongoParty.db(server_id).find(condition)

        MongoParty.db(server_id).update_many(
            {},
            {'$set': {'talent_id': 0}}
        )

        for doc in docs:
            # 天赋过期,删除加成
            Club(server_id, doc['_id']).force_load_staffs(send_notify=True)

    def get_talent_effects(self):
        if self.doc['talent_id']:
            return [self.doc['talent_id']]
        return []

    def get_remained_create_times(self):
        times = ValueLogPartyCreateTimes(self.server_id, self.char_id).count_of_today()
        remained = MAX_CREATE_TIMES - times
        if remained < 0:
            remained = 0

        return remained

    def get_remained_join_times(self):
        times = ValueLogPartyJoinTimes(self.server_id, self.char_id).count_of_today()
        remained = MAX_JOIN_TIMES - times
        if remained < 0:
            remained = 0

        return remained

    def get_info(self):
        return {
            'max_buy_times': GlobalConfig.value("PARTY_BUY_MAX_TIMES"),
            'remained_create_times': self.get_remained_create_times(),
            'remained_join_times': self.get_remained_join_times(),
            'talent_id': self.doc['talent_id'],
        }

    def create(self, party_level):
        ret = api_handle.API.Party.CreateDone()
        ret.ret = 0

        config = ConfigPartyLevel.get(party_level)
        if not config:
            ret.ret = ConfigErrorMessage.get_error_id("INVALID_OPERATE")
            return ret

        try:
            Union(self.server_id, self.char_id).check_level(config.need_union_level)
            cost = [(money_text_to_item_id('diamond'), config.need_diamond), ]
            rc = ResourceClassification.classify(cost)
            rc.check_exist(self.server_id, self.char_id)
        except GameException as e:
            ret.ret = e.error_id
            return ret

        return ret

    def start(self, party_level, member_ids):
        # member_ids 只是组员， 不包括创建者自己
        ret = api_handle.API.Party.StartDone()
        ret.ret = 0

        config = ConfigPartyLevel.get(party_level)
        try:
            cost = [(money_text_to_item_id('diamond'), config.need_diamond), ]
            rc = ResourceClassification.classify(cost)
            rc.check_exist(self.server_id, self.char_id)
            rc.remove(self.server_id, self.char_id)
        except GameException as e:
            ret.ret = e.error_id
            return ret

        ValueLogPartyCreateTimes(self.server_id, self.char_id).record()
        ValueLogPartyEngageTimes(self.server_id, self.char_id).record()
        for mid in member_ids:
            ValueLogPartyJoinTimes(self.server_id, mid).record()
            ValueLogPartyEngageTimes(self.server_id, self.char_id).record()

        return ret

    def buy_item(self, party_level, buy_id, member_ids):
        ret = api_handle.API.Party.BuyDone()
        ret.ret = 0

        config = ConfigPartyLevel.get(party_level)
        if buy_id not in [config.buy_one, config.buy_two]:
            ret.ret = ConfigErrorMessage.get_error_id("PARTY_BUY_ITEM_NOT_EXIST")
            return ret

        config_buy = ConfigPartyBuyItem.get(buy_id)

        try:
            rc = ResourceClassification.classify(config_buy.cost)
            rc.check_exist(self.server_id, self.char_id)
            rc.remove(self.server_id, self.char_id)
        except GameException as e:

            ret.ret = e.error_id
            return ret

        # 把购买的物品加给所有人
        item_id, item_amount = config_buy.buy_result()
        reward = [(item_id, item_amount), ]
        rc = ResourceClassification.classify(reward)

        rc.add(self.server_id, self.char_id)

        for mid in member_ids:
            rc.add(self.server_id, mid)

        ret.buy_name = config_buy.name
        ret.item_name = ConfigItemNew.get(item_id).name
        ret.item_amount = item_amount
        return ret

    def end(self, party_level, member_ids):
        ret = api_handle.API.Party.EndDone()
        ret.ret = 0

        config = ConfigPartyLevel.get(party_level)
        talent_id = random.choice(config.talent_skills)
        self.doc['talent_id'] = talent_id

        MongoParty.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'talent_id': talent_id
            }}
        )

        # apply talent_id to club
        Club(self.server_id, self.char_id).force_load_staffs(send_notify=True)

        reward = [(config.item_id, 1), ]
        rc = ResourceClassification.classify(reward)
        attachment = rc.to_json()

        char_ids = [self.char_id]
        char_ids.extend(member_ids)
        for c in char_ids:
            m = MailManager(self.server_id, c)
            m.add(config.mail_title, config.mail_content, attachment=attachment)

        ret.talent_id = talent_id
        return ret

    def send_notify(self):
        notify = PartyNotify()
        start_at, close_at = get_party_open_time_range(1, 23)

        notify_range = notify.time_range.add()

        notify_range.start_at = start_at.timestamp
        notify_range.close_at = close_at.timestamp

        notify.talent_id = self.doc['talent_id']
        notify.talent_end_at = get_time_of_tomorrow(12).timestamp
        notify.remained_create_times = self.get_remained_create_times()
        notify.remained_join_times = self.get_remained_join_times()

        MessagePipe(self.char_id).put(msg=notify)
