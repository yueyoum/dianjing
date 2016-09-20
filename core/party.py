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
from core.union import Union
from core.resource import ResourceClassification, money_text_to_item_id
from core.mail import MailManager
from core.value_log import ValueLogPartyCreateTimes, ValueLogPartyJoinTimes

from utils.api import APIReturn
from utils.message import MessagePipe
from utils.functional import get_start_time_of_today

from config import ConfigErrorMessage, ConfigPartyLevel, ConfigPartyBuyItem, ConfigItemNew

from protomsg.party_pb2 import PartyOpenTimeNotify

# 这部分功能都是 socket 发来的调用

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

    def get_info(self):
        return {
            'create_times': ValueLogPartyCreateTimes(self.server_id, self.char_id).count_of_today(),
            'join_times': ValueLogPartyJoinTimes(self.server_id, self.char_id).count_of_today(),
            'talent_id': self.doc['talent_id'],
        }

    def create(self, party_level):
        ret = APIReturn(self.char_id)

        config = ConfigPartyLevel.get(party_level)
        if not config:
            ret.code = ConfigErrorMessage.get_error_id("INVALID_OPERATE")
            return ret.normalize()

        try:
            Union(self.server_id, self.char_id).check_level(config.need_union_level)
            cost = [(money_text_to_item_id('diamond'), config.need_diamond), ]
            rc = ResourceClassification.classify(cost)
            rc.check_exist(self.server_id, self.char_id)
            rc.remove(self.server_id, self.char_id)
        except GameException as e:
            ret.code = e.error_id
            return ret.normalize()

        return ret.normalize()


    def start(self, party_level, member_ids):
        # member_ids 只是组员， 不包括创建者自己
        ret = APIReturn(self.char_id)

        ValueLogPartyCreateTimes(self.server_id, self.char_id).record()
        for mid in member_ids:
            ValueLogPartyJoinTimes(self.server_id, mid).record()

        return ret.normalize()

    def buy_item(self, party_level, buy_id, member_ids):
        ret = APIReturn(self.char_id)

        config = ConfigPartyLevel.get(party_level)
        if buy_id not in [config.buy_one, config.buy_two]:
            ret.code = ConfigErrorMessage.get_error_id("PARTY_BUY_ITEM_NOT_EXIST")
            return ret.normalize()

        config_buy = ConfigPartyBuyItem.get(buy_id)

        try:
            rc = ResourceClassification.classify(config_buy.cost)
            rc.check_exist(self.server_id, self.char_id)
            rc.remove(self.server_id, self.char_id)
        except GameException as e:

            ret.code = e.error_id
            return ret.normalize()

        # 把购买的物品加给所有人
        item_id, item_amount = config_buy.buy_result()
        reward = [(item_id, item_amount), ]
        rc = ResourceClassification.classify(reward)

        rc.add(self.server_id, self.char_id)

        for mid in member_ids:
            rc.add(self.server_id, mid)

            ret.add_other_char(mid)

        ret.set_data('buy_name', config_buy.name)
        ret.set_data('item_name', ConfigItemNew.get(item_id).name)
        return ret.normalize()

    def end(self, party_level, member_ids):
        ret = APIReturn(self.char_id)

        config = ConfigPartyLevel.get(party_level)
        talent_id = random.choice(config.talent_skills)
        self.doc['talent_id'] = talent_id

        MongoParty.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'talent_id': talent_id
            }}
        )

        reward = [(config.item_id, 1), ]
        rc = ResourceClassification.classify([reward])
        attachment = rc.to_json()

        char_ids = member_ids.append(self.char_id)
        for c in char_ids:
            m = MailManager(self.server_id, c)
            m.add(config.mail_title, config.mail_content, attachment=attachment)

        for c in member_ids:
            ret.add_other_char(c)

        ret.set_data('talent_id', talent_id)
        return ret.normalize()


    def send_notify(self):
        notify = PartyOpenTimeNotify()
        start_at, close_at = get_party_open_time_range(1, 23)
        notify.start_at = start_at.timestamp
        notify.close_at = close_at.timestamp

        MessagePipe(self.char_id).put(msg=notify)


def get_party_open_time_range(h1, h2):
    today = get_start_time_of_today()

    time1 = today.replace(hours=h1)
    time2 = today.replace(hours=h2)

    return time1, time2
