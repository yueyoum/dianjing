# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       vip
Date Created:   2016-05-24 11-47
Description:

"""

from dianjing.exception import GameException

from core.mongo import MongoVIP
from core.resource import ResourceClassification, money_text_to_item_id

from utils.message import MessagePipe

from config import ConfigVIP, ConfigErrorMessage

from protomsg.vip_pb2 import VIPNotify

MAX_VIP_LEVEL = max(ConfigVIP.INSTANCES.keys())


class VIP(object):
    __slots__ = ['server_id', 'char_id', 'doc']
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.doc = MongoVIP.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoVIP.document()
            self.doc['_id'] = self.char_id
            MongoVIP.db(self.server_id).insert_one(self.doc)


    def add_exp(self, exp):
        self.doc['exp'] += exp

        while True:
            if self.doc['vip'] >= MAX_VIP_LEVEL:
                self.doc['vip'] = MAX_VIP_LEVEL
                if self.doc['exp'] >= ConfigVIP.get(MAX_VIP_LEVEL).exp:
                    self.doc['exp'] = ConfigVIP.get(MAX_VIP_LEVEL).exp - 1

                break

            need_exp = ConfigVIP.get(self.doc['vip']).exp
            if self.doc['exp'] < need_exp:
                break

            self.doc['exp'] -= need_exp
            self.doc['vip'] += 1

        MongoVIP.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'vip': self.doc['vip'],
                'exp': self.doc['exp'],
            }}
        )

        self.send_notify()

    def buy_reward(self, vip_level):
        config = ConfigVIP.get(vip_level)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if vip_level in self.doc['rewards']:
            raise GameException(ConfigErrorMessage.get_error_id("VIP_ALREADY_BUY_REWARD"))

        needs = [(money_text_to_item_id('diamond'), config.diamond_now)]
        rc = ResourceClassification.classify(needs)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id)

        got = [(config.item_id, 1)]
        rc = ResourceClassification.classify(got)
        rc.add(self.server_id, self.char_id)
        return rc


    def send_notify(self):
        notify = VIPNotify()
        notify.vip = self.doc['vip']
        notify.exp = self.doc['exp']
        notify.rewarded.extend(self.doc['rewards'])

        MessagePipe(self.char_id).put(msg=notify)