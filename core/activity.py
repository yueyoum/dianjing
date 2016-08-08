# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       activity
Date Created:   2016-08-05 15:21
Description:

"""

import arrow
from dianjing.exception import GameException

from core.mongo import MongoActivityNewPlayer

from core.club import Club
from core.resource import ResourceClassification, money_text_to_item_id

from utils.message import MessagePipe

from config import ConfigErrorMessage, ConfigActivityNewPlayer, ConfigActivityDailyBuy, ConfigTaskCondition

from protomsg.activity_pb2 import (
    ACTIVITY_COMPLETE,
    ACTIVITY_DOING,
    ACTIVITY_REWARD,
    ActivityNewPlayerDailyBuyNotify,
    ActivityNewPlayerNotify,
)
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE


class ActivityNewPlayer(object):
    __slots__ = ['server_id', 'char_id', 'doc', 'create_day']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.doc = MongoActivityNewPlayer.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoActivityNewPlayer.document()
            self.doc['_id'] = self.char_id
            MongoActivityNewPlayer.db(self.server_id).insert_one(self.doc)

        self.create_day = Club.create_days(server_id, char_id)

    def get_activity_status(self, _id, end_at=None):
        """

        :rtype: (int, int)
        """

        if end_at:
            # 新手任务的时间范围就是创建那一刻到现在
            end_at = arrow.utcnow().timestamp

        config = ConfigActivityNewPlayer.get(_id)
        config_condition = ConfigTaskCondition.get(config.condition_id)
        value = config_condition.get_value(self.server_id, self.char_id, start_at=None, end_at=end_at)

        if _id in self.doc['done']:
            return value, ACTIVITY_COMPLETE

        if config_condition.compare_value(value, config.condition_value):
            return value, ACTIVITY_REWARD

        return value, ACTIVITY_DOING

    def trig(self, condition_id):
        ids = ConfigActivityNewPlayer.get_activity_ids_by_condition_id(condition_id)
        if not ids:
            return

        self.send_notify(ids=ids)

    def get_reward(self, _id):
        config = ConfigActivityNewPlayer.get(_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if config.day > self.create_day:
            raise GameException(ConfigErrorMessage.get_error_id("ACTIVITY_NEW_PLAYER_DAY_NOT_ARRIVE"))

        _, status = self.get_activity_status(_id)
        if status == ACTIVITY_COMPLETE:
            raise GameException(ConfigErrorMessage.get_error_id("ACTIVITY_NEW_PLAYER_HAS_GOT"))

        if status == ACTIVITY_DOING:
            raise GameException(ConfigErrorMessage.get_error_id("ACTIVITY_NEW_PLAYER_CONDITION_NOT_SATISFY"))

        rc = ResourceClassification.classify(config.rewards)
        rc.add(self.server_id, self.char_id)

        self.doc['done'].append(_id)
        MongoActivityNewPlayer.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$push': {
                'done': _id
            }}
        )

        self.send_notify(ids=[_id])

        return rc

    def daily_buy(self):
        config = ConfigActivityDailyBuy.get(self.create_day)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if self.create_day in self.doc['daily_buy']:
            raise GameException(ConfigErrorMessage.get_error_id("ACTIVITY_DAILY_BUY_HAS_BOUGHT"))

        cost = [(money_text_to_item_id('diamond'), config.diamond_now), ]

        rc = ResourceClassification.classify(cost)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id)

        rc = ResourceClassification.classify(config.items)
        rc.add(self.server_id, self.char_id)

        self.doc['daily_buy'].append(self.create_day)
        MongoActivityNewPlayer.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$push': {
                'daily_buy': self.create_day
            }}
        )

        self.send_daily_buy_notify()
        return rc

    def send_daily_buy_notify(self):
        if self.create_day >= 8:
            return

        notify = ActivityNewPlayerDailyBuyNotify()
        for i in range(1, self.create_day+1):
            notify_status = notify.status.add()
            notify_status.day = i
            notify_status.has_bought = i in self.doc['daily_buy']

        MessagePipe(self.char_id).put(msg=notify)

    def send_notify(self, ids=None):
        if self.create_day >= 8:
            return

        if ids:
            act = ACT_UPDATE
        else:
            act = ACT_INIT
            ids = ConfigActivityNewPlayer.INSTANCES.keys()

        end_at = arrow.utcnow().timestamp

        notify = ActivityNewPlayerNotify()
        notify.act = act
        for i in ids:
            # 后面天数的情况不发
            if ConfigActivityNewPlayer.get(i).day > self.create_day:
                continue

            value, status = self.get_activity_status(i, end_at=end_at)

            notify_items = notify.items.add()
            notify_items.id = i
            notify_items.current_value = value
            notify_items.status = status

        MessagePipe(self.char_id).put(msg=notify)
