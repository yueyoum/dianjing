# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       store
Date Created:   2015-11-12 16:01
Description:

"""

import random

import arrow
from django.conf import settings

from dianjing.exception import GameException
from core.mongo import MongoLadder
from core.common import CommonLadderStore
from core.character import Character
from core.lock import LadderStoreLock
from utils.message import MessagePipe, MessageFactory
from config import (
    ConfigLadderScoreStore,
    ConfigErrorMessage,
)
from protomsg.ladder_pb2 import LadderStoreNotify


def make_notify_protomsg(items):
    next_day = arrow.utcnow().to(settings.TIME_ZONE).replace(days=1)
    next_time = arrow.Arrow(next_day.year, next_day.month, next_day.day).timestamp

    notify = LadderStoreNotify()
    notify.next_refresh_time = next_time
    notify.ids.extend(items)
    return notify


# 必须在Ladder后面初始化
class LadderStore(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.items = self.get_items()

    @staticmethod
    def cronjob(server_id):
        # 每天刷新物品和购买次数
        MongoLadder.db(server_id).update_many(
            {},
            {'$set': {
                'store_items': [],
                'buy_times': {},
            }}
        )

        with LadderStoreLock(server_id).lock():
            items = random.sample(ConfigLadderScoreStore.INSTANCES.keys(), 9)
            CommonLadderStore.set(server_id, items)

        notify = make_notify_protomsg(items)
        data = MessageFactory.pack(notify)
        char_ids = Character.get_recent_login_char_ids(server_id)
        for cid in char_ids:
            MessagePipe(cid).put(data=data)

    def refresh_by_self(self):
        self.items = random.sample(ConfigLadderScoreStore.INSTANCES.keys(), 9)
        MongoLadder.db(self.server_id).update_one(
            {'_id': str(self.char_id)},
            {'$set': {
                'store_items': self.items,
                'buy_times': {},
            }}
        )

        self.send_notify()

    def get_items(self):
        doc = MongoLadder.db(self.server_id).find_one(
            {'_id': str(self.char_id)},
            {'store_items': 1}
        )

        items = doc.get('store_items', [])
        if items:
            return items

        items = CommonLadderStore.get(self.server_id)
        if not items:
            with LadderStoreLock(self.server_id).lock():
                items = random.sample(ConfigLadderScoreStore.INSTANCES.keys(), 9)
                CommonLadderStore.set(self.server_id, items)

        return items

    def buy(self, item_id):
        from core.ladder import Ladder
        ladder = Ladder(self.server_id, self.char_id)

        if item_id not in self.items:
            raise GameException(ConfigErrorMessage.get_error_id("STORE_ITEM_NOT_EXIST"))

        doc = MongoLadder.db(self.server_id).find_one(
            {'_id': str(self.char_id)},
            {'buy_times': 1, 'score': 1}
        )

        config = ConfigLadderScoreStore.get(item_id)
        if config.times_limit == 0:
            raise GameException(ConfigErrorMessage.get_error_id("STORE_ITEM_CANNOT_BUY"))

        if config.times_limit > 0:
            # has limit
            if doc.get('buy_times', {}).get(str(item_id), 0) >= config.times_limit:
                raise GameException(ConfigErrorMessage.get_error_id("STORE_ITEM_REACH_LIMIT"))

        if doc['score'] < config.score:
            raise GameException(ConfigErrorMessage.get_error_id("LADDER_SCORE_NOT_ENOUGH"))

        MongoLadder.db(self.server_id).update_one(
            {'_id': str(self.char_id)},
            {
                '$inc': {
                    'buy_times.{0}'.format(item_id): 1,
                    'score': -config.score
                },
            }
        )

        # ItemManager(self.server_id, self.char_id).add_item(config.item, amount=config.item_amount)
        ladder.send_notify()

    def send_notify(self):
        notify = make_notify_protomsg(self.items)
        MessagePipe(self.char_id).put(msg=notify)
