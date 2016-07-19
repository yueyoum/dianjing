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
from core.signals import vip_level_up_signal

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

    @property
    def level(self):
        return self.doc['vip']

    def check(self, need_vip):
        if self.doc['vip'] < need_vip:
            raise GameException(ConfigErrorMessage.get_error_id("VIP_LEVEL_NOT_ENOUGH"))

    def add_exp(self, exp):
        old_vip = self.doc['vip']
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

        if self.doc['vip'] > old_vip:
            vip_level_up_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
                new_level=self.doc['vip']
            )

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

        self.doc['rewards'].append(vip_level)
        MongoVIP.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'rewards': self.doc['rewards']
            }}
        )

        self.send_notify()
        return rc

    def send_notify(self):
        notify = VIPNotify()
        notify.vip = self.doc['vip']
        notify.exp = self.doc['exp']
        notify.rewarded.extend(self.doc['rewards'])

        MessagePipe(self.char_id).put(msg=notify)

    @property
    def challenge_reset_times(self):
        return ConfigVIP.get(self.doc['vip']).challenge_reset_times

    @property
    def dungeon_reset_times(self):
        return ConfigVIP.get(self.doc['vip']).daily_dungeon_reset_times

    @property
    def tower_reset_times(self):
        return ConfigVIP.get(self.doc['vip']).tower_reset_times

    @property
    def arena_buy_times(self):
        return ConfigVIP.get(self.doc['vip']).arena_buy_times

    @property
    def energy_buy_times(self):
        return ConfigVIP.get(self.doc['vip']).energy_buy_times

    @property
    def store_refresh_times(self):
        return ConfigVIP.get(self.doc['vip']).store_refresh_times

    @property
    def territory_help_times(self):
        return ConfigVIP.get(self.doc['vip']).territory_help_times

    @property
    def arena_search_reset_times(self):
        return ConfigVIP.get(self.doc['vip']).arena_search_reset_times
