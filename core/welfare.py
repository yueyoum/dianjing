# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       welfare
Date Created:   2016-06-28 15-58
Description:

"""

import arrow

from django.conf import settings

from dianjing.exception import GameException

from core.mongo import MongoWelfare
from core.club import get_club_property, Club
from core.vip import VIP
from core.value_log import ValueLogWelfareSignInTimes, ValueLogWelfareEnergyRewardTimes
from core.resource import ResourceClassification

from utils.message import MessagePipe

from config import (
    ConfigWelfareLevelReward,
    ConfigWelfareNewPlayer,
    ConfigWelfareSignIn,
    ConfigErrorMessage,
    ConfigItemUse,
)

from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT
from protomsg.welfare_pb2 import (
    WELFARE_CAN_GET,
    WELFARE_HAS_GOT,
    WELFARE_CAN_NOT,
    WelfareEnergyRewardNotify,
    WelfareLevelRewardNotify,
    WelfareNewPlayerNotify,
    WelfareSignInNotify,
)

ENERGY_TIME_RANGE = (
    (12, 14),
    (18, 20),
)


class Welfare(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.doc = MongoWelfare.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoWelfare.document()
            self.doc['_id'] = self.char_id
            self.doc['signin'] = ConfigWelfareSignIn.FIRST_DAY - 1
            MongoWelfare.db(self.server_id).insert_one(self.doc)

    def signin(self):
        today_times = ValueLogWelfareSignInTimes(self.server_id, self.char_id).count_of_today()
        if today_times > 0:
            raise GameException(ConfigErrorMessage.get_error_id("WELFARE_ALREADY_SIGNED"))

        day = self.doc['signin'] + 1
        if day == ConfigWelfareSignIn.LAST_DAY:
            self.doc['signin'] = ConfigWelfareSignIn.FIRST_DAY - 1
        else:
            self.doc['signin'] = day

        config = ConfigWelfareSignIn.get(day)

        reward = []
        reward.extend(config.reward)

        if VIP(self.server_id, self.char_id).level >= config.vip:
            reward.extend(config.vip_reward)

        rc = ResourceClassification.classify(reward)
        rc.add(self.server_id, self.char_id)

        MongoWelfare.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'signin': self.doc['signin']
            }}
        )

        ValueLogWelfareEnergyRewardTimes(self.server_id, self.char_id).record()
        self.send_signin_notify()
        return rc

    def send_signin_notify(self):
        today_times = ValueLogWelfareSignInTimes(self.server_id, self.char_id).count_of_today()

        notify = WelfareSignInNotify()
        notify.day = self.doc['signin'] + 1
        notify.signed = today_times > 0
        MessagePipe(self.char_id).put(msg=notify)

    def get_new_player_item_status(self, _id, login_days=None):
        if _id in self.doc['new_player']:
            return WELFARE_HAS_GOT

        if login_days is None:
            login_days = Club.create_days(self.server_id, self.char_id)

        if login_days >= _id:
            return WELFARE_CAN_GET

        return WELFARE_CAN_NOT

    def get_level_reward_item_status(self, _id, level=None):
        if _id in self.doc['level_reward']:
            return WELFARE_HAS_GOT

        if level is None:
            level = get_club_property(self.server_id, self.char_id, 'level')

        if level >= _id:
            return WELFARE_CAN_GET

        return WELFARE_CAN_NOT

    def new_player_get(self, _id):
        config = ConfigWelfareNewPlayer.get(_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        status = self.get_new_player_item_status(_id)
        if status == WELFARE_CAN_NOT:
            raise GameException(ConfigErrorMessage.get_error_id("WELFARE_NEW_PLAYER_CAN_NOT"))

        if status == WELFARE_HAS_GOT:
            raise GameException(ConfigErrorMessage.get_error_id("WELFARE_NEW_PLAYER_HAS_GOT"))

        self.doc['new_player'].append(_id)

        rc = ResourceClassification.classify(config.reward)
        rc.add(self.server_id, self.char_id)

        MongoWelfare.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$push': {
                'new_player': _id
            }}
        )

        self.send_new_player_notify(_id)
        return rc

    def level_reward_get(self, _id):
        config = ConfigWelfareLevelReward.get(_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        status = self.get_level_reward_item_status(_id)
        if status == WELFARE_CAN_NOT:
            raise GameException(ConfigErrorMessage.get_error_id("WELFARE_LEVEL_REWARD_CAN_NOT"))

        if status == WELFARE_HAS_GOT:
            raise GameException(ConfigErrorMessage.get_error_id("WELFARE_LEVEL_REWARD_HAS_GOT"))

        self.doc['level_reward'].append(_id)

        rc = ResourceClassification.classify(config.reward)
        rc.add(self.server_id, self.char_id)

        MongoWelfare.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$push': {
                'level_reward': _id
            }}
        )

        self.send_level_reward_notify(_id)
        return rc

    def energy_reward_get(self):
        hour = arrow.utcnow().to(settings.TIME_ZONE).hour

        for index, (start, end) in ENERGY_TIME_RANGE:
            if start <= hour <= end:
                times = ValueLogWelfareEnergyRewardTimes(self.server_id, self.char_id).count_of_today(sub_id=index)
                if times > 0:
                    raise GameException(ConfigErrorMessage.get_error_id("WELFARE_ENERGY_ALREADY_GOT"))

                ValueLogWelfareEnergyRewardTimes(self.server_id, self.char_id).record(sub_id=index)

                config = ConfigItemUse.get(-1)
                items = config.using_result()
                rc = ResourceClassification.classify(items)
                rc.add(self.server_id, self.char_id)

                self.send_energy_reward_notify()
                return rc

        raise GameException(ConfigErrorMessage.get_error_id("WELFARE_ENERGY_CAN_NOT_GET_NOT_IN_TIME"))

    def send_new_player_notify(self, _id=None):
        if _id:
            act = ACT_UPDATE
            ids = [_id]
        else:
            act = ACT_INIT
            ids = ConfigWelfareNewPlayer.INSTANCES.keys()

        login_days = Club.create_days(self.server_id, self.char_id)

        notify = WelfareNewPlayerNotify()
        notify.act = act
        for i in ids:
            notify_item = notify.items.add()
            notify_item.id = i
            notify_item.status = self.get_new_player_item_status(i, login_days=login_days)

        MessagePipe(self.char_id).put(msg=notify)

    def send_level_reward_notify(self, _id=None):
        if _id:
            act = ACT_UPDATE
            ids = [_id]
        else:
            act = ACT_INIT
            ids = ConfigWelfareLevelReward.INSTANCES.keys()

        level = get_club_property(self.server_id, self.char_id, 'level')

        notify = WelfareLevelRewardNotify()
        notify.act = act
        for i in ids:
            notify_item = notify.items.add()
            notify_item.id = i
            notify_item.status = self.get_level_reward_item_status(i, level=level)

        MessagePipe(self.char_id).put(msg=notify)

    def send_energy_reward_notify(self):
        notify = WelfareEnergyRewardNotify()
        for index, (start, end) in enumerate(ENERGY_TIME_RANGE):
            notify_range = notify.time_range.add()
            notify_range.start = start
            notify_range.end = end

            times = ValueLogWelfareEnergyRewardTimes(self.server_id, self.char_id).count_of_today(sub_id=index)
            notify_range.can_get = times == 0

        MessagePipe(self.char_id).put(msg=notify)
