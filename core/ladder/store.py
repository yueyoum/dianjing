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
from core.item import ItemManager
from core.lock import LadderStoreLock
from utils.message import MessagePipe
from config import (
    ConfigLadderScoreStore,
    ConfigErrorMessage,
)
from protomsg.ladder_pb2 import LadderStoreNotify


class LadderStore(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.items = LadderStore.refresh(self.server_id)

    @staticmethod
    def cronjob(server_id):
        # 每天刷新购买次数
        MongoLadder.db(server_id).update_many(
            {},
            {'$set': {'buy_times': {}}}
        )

    @staticmethod
    def refresh(server_id, force=False):
        with LadderStoreLock(server_id).lock():
            items = CommonLadderStore.get(server_id)
            if not force and items:
                return items

            items = random.sample(ConfigLadderScoreStore.INSTANCES.keys(), 9)
            CommonLadderStore.set(server_id, items)

        return items

    def buy(self, item_id):
        from core.ladder import Ladder
        ladder = Ladder(self.server_id, self.char_id)

        if item_id not in self.items:
            raise GameException(ConfigErrorMessage.get_error_id("LADDER_STORE_ITEM_NOT_EXIST"))

        doc = MongoLadder.db(self.server_id).find_one(
            {'_id': str(self.char_id)},
            {'buy_times': 1, 'score': 1}
        )

        config = ConfigLadderScoreStore.get(item_id)
        if config.times_limit == 0:
            raise GameException(ConfigErrorMessage.get_error_id("LADDER_SCORE_CANNOT_BUY"))

        if config.times_limit > 0:
            # has limit
            if doc.get('buy_times', {}).get(str(item_id), 0) >= config.times_limit:
                raise GameException(ConfigErrorMessage.get_error_id("LADDER_STORE_ITEM_REACH_LIMIT"))

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

        ItemManager(self.server_id, self.char_id).add_item(config.item, config.item_amount)
        ladder.send_notify()

    def send_notify(self):
        next_day = arrow.utcnow().to(settings.TIME_ZONE).replace(days=1)
        next_time = arrow.Arrow(next_day.year, next_day.month, next_day.day).timestamp

        notify = LadderStoreNotify()
        notify.next_refresh_time = next_time
        notify.ids.extend(self.items)

        MessagePipe(self.char_id).put(msg=notify)
