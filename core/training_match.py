# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training_match
Date Created:   2015-12-08 16:16
Description:    训练赛

"""

import random
import arrow

from django.conf import settings

from dianjing.exception import GameException

from core.mongo import MongoTrainingMatch
from core.character import Character
from core.club import Club
from core.resource import Resource
from core.match import ClubMatch
from core.staff import StaffManger
from core.common import CommonTrainingMatchStore
from core.lock import TrainingMatchStoreLock

from utils.message import MessagePipe, MessageFactory

from config import ConfigTrainingMatchReward, ConfigErrorMessage, ConfigNPC, ConfigTrainingMatchStore

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.training_match_pb2 import (
    TRAINING_MATCH_CLUB_FAIL,
    TRAINING_MATCH_CLUB_NOT_OPEN,
    TRAINING_MATCH_CLUB_OPEN,
    TRAINING_MATCH_CLUB_PASS,
    TrainingMatchNotify,
    TrainingMatchStoreNotify,
)

MAX_RELIVE_TIMES = 3
RELIVE_COST_DIAMOND = 20

MAX_MATCH_CLUB_INDEX = 13
MAX_MATCH_CLUB = 14


class TrainingMatch(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoTrainingMatch.exist(self.server_id, self.char_id):
            self.generate()

    @staticmethod
    def cronjob(server_id):
        MongoTrainingMatch.db(server_id).drop()

    def generate(self):
        clubs = []
        """:type: list[core.club.Club]"""

        for i in range(MAX_MATCH_CLUB):
            match_club = Club(self.server_id, self.char_id)
            match_club.name = random.choice(ConfigNPC.CLUB_NAMES)
            match_club.manager_name = random.choice(ConfigNPC.MANAGER_NAMES)

            clubs.append(match_club)

        multiple = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]

        for i in range(MAX_MATCH_CLUB):
            clubs[i].change_staff_strengthen(multiple[i])

        doc = MongoTrainingMatch.document()
        doc['_id'] = self.char_id
        doc['status'] = {'0': TRAINING_MATCH_CLUB_OPEN}
        doc['clubs'] = [c.dumps() for c in clubs]

        MongoTrainingMatch.db(self.server_id).insert_one(doc)

    def add_score(self, score):
        MongoTrainingMatch.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {'score': score}}
        )
        self.send_notify()

    def start(self, index):
        if index > MAX_MATCH_CLUB_INDEX:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_MATCH_NOT_EXIST"))

        doc = self.get_training_match_data()

        status = doc['status'].get(str(index), None)
        if status is None:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_MATCH_NOT_OPEN"))

        if status == TRAINING_MATCH_CLUB_PASS:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_MATCH_ALREADY_PASSED"))

        if status == TRAINING_MATCH_CLUB_FAIL:
            if doc['relive_times'] >= MAX_RELIVE_TIMES:
                raise GameException(ConfigErrorMessage.get_error_id("TRAINING_MATCH_RELIVE_NO_TIMES"))

            message = u"Training Match relive for {0}".format(index)
            with Resource(self.server_id, self.char_id).check(diamond=-RELIVE_COST_DIAMOND, message=message):
                MongoTrainingMatch.db(self.server_id).update_one(
                    {'_id': self.char_id},
                    {'$inc': {'relive_times': 1}}
                )

        club = Club(self.server_id, self.char_id)
        club_data = doc['clubs'][index]
        opposite_club = Club.loads(club_data)

        match = ClubMatch(club, opposite_club)

        msg = match.start()
        msg.key = self.make_match_key(index, opposite_club.char_id)
        return msg

    def make_match_key(self, index, target_id):
        return "%s,%s,%s,%s" % (arrow.utcnow().timestamp, index, self.char_id, target_id)

    def get_training_match_data(self):
        return MongoTrainingMatch.db(self.server_id).find_one({'_id': self.char_id})

    def match_report(self, is_win, key):
        timestamp, index, club_one, club_two = str(key).split(',')

        tmp_drop = None
        updater = {}
        updated_ids = []

        # if is_win:
        #     index = int(index)
        #     updated_ids = [index]
        #     config_id = index + 1
        #
        #     if not ConfigTrainingMatchReward.get(config_id):
        #         raise GameException(ConfigErrorMessage.get_error_id("TRAINING_MATCH_NOT_EXIST"))
        #
        #     reward_config = ConfigTrainingMatchReward.get(config_id)
        #     tmp_drop = Drop.generate(reward_config.reward)
        #     tmp_drop.training_match_score = reward_config.score
        #
        #     message = "Training Match {0} drop".format(index)
        #     Resource(self.server_id, self.char_id).save_drop(tmp_drop, message=message)
        #
        #     updater['status.{0}'.format(index)] = TRAINING_MATCH_CLUB_PASS
        #
        #     if index < MAX_MATCH_CLUB_INDEX:
        #         next_index = index + 1
        #         updated_ids.append(next_index)
        #         updater['status.{0}'.format(next_index)] = TRAINING_MATCH_CLUB_OPEN
        # else:
        #     updater['status.{0}'.format(index)] = TRAINING_MATCH_CLUB_FAIL
        #
        # MongoTrainingMatch.db(self.server_id).update_one(
        #     {'_id': self.char_id},
        #     {'$set': updater}
        # )
        #
        # self.send_notify(ids=updated_ids)
        #
        # if tmp_drop:
        #     return tmp_drop.make_protomsg()

    def get_match_detail(self, index):
        doc = self.get_training_match_data()
        staff_ids = Club.loads(doc['clubs'][index]).match_staffs
        return StaffManger(self.server_id, self.char_id).get_dict_of_staff_object_by_ids(staff_ids)

    def send_notify(self, ids=None):
        if ids:
            act = ACT_UPDATE
        else:
            act = ACT_INIT
            ids = [i - 1 for i in ConfigTrainingMatchReward.INSTANCES.keys()]

        doc = self.get_training_match_data()

        notify = TrainingMatchNotify()
        notify.act = act
        notify.remained_relive_times = MAX_RELIVE_TIMES - doc['relive_times']
        notify.relive_cost = RELIVE_COST_DIAMOND
        notify.score = doc.get('score', 0)

        for i in ids:
            club = Club.loads(doc['clubs'][i])

            notify_club = notify.clubs.add()
            notify_club.index = i
            notify_club.flag = club.flag
            notify_club.name = club.name
            notify_club.level = club.level
            notify_club.power = club.get_power()

            status = doc['status'].get(str(i), None)
            if status is None:
                notify_club.status = TRAINING_MATCH_CLUB_NOT_OPEN
            else:
                notify_club.status = status

        MessagePipe(self.char_id).put(msg=notify)


def make_store_notify_protomsg(items):
    next_day = arrow.utcnow().to(settings.TIME_ZONE).replace(days=1)
    next_time = arrow.Arrow(next_day.year, next_day.month, next_day.day).timestamp

    notify = TrainingMatchStoreNotify()
    notify.next_refresh_time = next_time
    notify.ids.extend(items)
    return notify


class TrainingMatchStore(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.items = self.get_items()

    @staticmethod
    def cronjob(server_id):
        # 每天刷新物品和购买次数
        MongoTrainingMatch.db(server_id).update_many(
            {},
            {'$set': {
                'store_items': [],
                'buy_times': {},
            }}
        )

        with TrainingMatchStoreLock(server_id).lock():
            items = random.sample(ConfigTrainingMatchStore.INSTANCES.keys(), 9)
            CommonTrainingMatchStore.set(server_id, items)

        notify = make_store_notify_protomsg(items)
        data = MessageFactory.pack(notify)
        char_ids = Character.get_recent_login_char_ids(server_id)
        for cid in char_ids:
            MessagePipe(cid).put(data=data)

    def refresh_by_self(self):
        self.items = random.sample(ConfigTrainingMatchStore.INSTANCES.keys(), 9)
        MongoTrainingMatch.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'store_items': self.items,
                'buy_times': {}
            }}
        )

        self.send_notify()

    def get_items(self):
        doc = MongoTrainingMatch.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'store_items': 1}
        )

        items = doc.get('store_items', [])
        if items:
            return items

        items = CommonTrainingMatchStore.get(self.server_id)
        if not items:
            with TrainingMatchStoreLock(self.server_id).lock():
                items = random.sample(ConfigTrainingMatchStore.INSTANCES.keys(), 9)
                CommonTrainingMatchStore.set(self.server_id, items)

        return items

    def buy(self, item_id):
        if item_id not in self.items:
            raise GameException(ConfigErrorMessage.get_error_id("STORE_ITEM_NOT_EXIST"))

        doc = MongoTrainingMatch.db(self.server_id).find_one(
            {'_id': str(self.char_id)},
            {'buy_times': 1, 'score': 1}
        )

        config = ConfigTrainingMatchStore.get(item_id)
        if config.times_limit == 0:
            raise GameException(ConfigErrorMessage.get_error_id("STORE_ITEM_CANNOT_BUY"))

        if config.times_limit > 0:
            # has limit
            if doc.get('buy_times', {}).get(str(item_id), 0) >= config.times_limit:
                raise GameException(ConfigErrorMessage.get_error_id("STORE_ITEM_REACH_LIMIT"))

        if doc['score'] < config.score:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_MATCH_SCORE_NOT_ENOUGH"))

        MongoTrainingMatch.db(self.server_id).update_one(
            {'_id': str(self.char_id)},
            {
                '$inc': {
                    'buy_times.{0}'.format(item_id): 1,
                    'score': -config.score
                },
            }
        )

        # ItemManager(self.server_id, self.char_id).add_item(config.item, amount=config.item_amount)
        TrainingMatch(self.server_id, self.char_id).send_notify()

    def send_notify(self):
        notify = make_store_notify_protomsg(self.items)
        MessagePipe(self.char_id).put(msg=notify)
