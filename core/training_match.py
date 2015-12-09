# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training_match
Date Created:   2015-12-08 16:16
Description:

"""

import random

from dianjing.exception import GameException

from core.mongo import MongoCharacter, MongoTrainingMatch

from core.club import Club
from core.package import Drop
from core.resource import Resource
from core.match import ClubMatch

from utils.message import MessagePipe

from config import ConfigTrainingMatchReward, ConfigErrorMessage, ConfigNPC

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.training_match_pb2 import (
    TRAINING_MATCH_CLUB_DONE,
    TRAINING_MATCH_CLUB_FAIL,
    TRAINING_MATCH_CLUB_NOT_OPEN,
    TRAINING_MATCH_CLUB_OPEN,
    TRAINING_MATCH_CLUB_PASS,
    TrainingMatchNotify,
)

RELIVE_TIMES = 3
RELIVE_DIAMOND = 20


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

        club = Club(self.server_id, self.char_id)

        min_level = club.level - 5
        if min_level < 1:
            min_level = 1

        max_level = club.level + 5

        condition = {
            '$and': [
                {'club.level': {'$gte': min_level}},
                {'club.level': {'$lte': max_level}}
            ]
        }

        # TODO, better method to find clubs
        char_docs = MongoCharacter.db(self.server_id).find(condition, {'club.level': 1}).sort({'club.level': 1}).limit(
            100)

        if char_docs.count() < 14:
            for doc in char_docs:
                clubs.append(Club(self.server_id, doc['_id']))

            need_amount = 14 - len(clubs)
            for i in range(need_amount):
                c = Club(self.server_id, self.char_id)
                c.name = random.choice(ConfigNPC.CLUB_NAMES)
                c.manager_name = random.choice(ConfigNPC.MANAGER_NAMES)

                clubs.append(c)
        else:
            char_ids = [(doc['_id'], doc['club']['level']) for doc in char_docs]
            char_ids = random.sample(char_ids, 14)
            char_ids.sort(key=lambda item: item[1])

            for cid, club_level in char_ids:
                c = Club(self.server_id, cid)
                if cid == self.char_id:
                    c.name = random.choice(ConfigNPC.CLUB_NAMES)
                    c.manager_name = random.choice(ConfigNPC.MANAGER_NAMES)

                clubs.append(c)

        multiple = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0]

        for i in range(14):
            clubs[i].change_staff_strengthen(multiple[i])

        doc = MongoTrainingMatch.document()
        doc['_id'] = self.char_id
        doc['status'] = {'1': 1}
        doc['clubs'] = [c.dumps() for c in clubs]

        MongoTrainingMatch.db(self.server_id).insert_one(doc)

    def start(self, index):
        config = ConfigTrainingMatchReward.get(index)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_MATCH_NOT_EXIST"))

        doc = MongoTrainingMatch.db(self.server_id).find_one({'_id': self.char_id})

        status = doc['status'].get(str(index), None)
        if status is None:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_MATCH_NOT_OPEN"))

        if status == 2:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_MATCH_ALREADY_PASSED"))

        if status == 3:
            if doc['relive_times'] >= RELIVE_TIMES:
                raise GameException(ConfigErrorMessage.get_error_id("TRAINING_MATCH_RELIVE_NO_TIMES"))

            message = u"Training Match relive for {0}".format(index)
            with Resource(self.server_id, self.char_id).check(diamond=-RELIVE_DIAMOND, message=message):
                MongoTrainingMatch.db(self.server_id).update_one(
                    {'_id': self.char_id},
                    {'$inc': {'relive_times': 1}}
                )

        club = Club(self.server_id, self.char_id)

        club_data = doc['clubs'][index - 1]
        opposite_club = Club.loads(club_data)

        match = ClubMatch(club, opposite_club)
        msg = match.start()

        drop = Drop()

        updated_ids = [index]
        if msg.club_one_win:
            drop = Drop.generate(ConfigTrainingMatchReward.get(index).reward)
            Resource(self.server_id, self.char_id).save_drop(drop, message="Training Match {0} drop".format(index))

            updater = {
                'status.{0}'.format(index): 2
            }

            if index < 14:
                updated_ids.append(index + 1)
                updater['status.{0}'.format(index + 1)] = 1
        else:
            updater = {
                'status.{0}'.format(index): 3
            }

        MongoTrainingMatch.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_notify(ids=updated_ids)

        return msg, drop.make_protomsg()

    def get_additional_reward(self, index):
        config = ConfigTrainingMatchReward.get(index)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_MATCH_NOT_EXIST"))

        if not config.additional_reward:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        doc = MongoTrainingMatch.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'status': 1, 'rewards': 1}
        )

        status = doc['status'].get(str(index), None)
        if status != 2:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_MATCH_NOT_PASS"))

        if index in doc['rewards']:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_MATCH_ALREADY_GET_REWARD"))

        drop = Drop.generate(config.additional_reward)
        Resource(self.server_id, self.char_id).save_drop(drop, message="Training Match {0} additional drop".format(index))

        MongoTrainingMatch.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$push': {'rewards': index}}
        )

        self.send_notify()
        return drop.make_protomsg()

    def send_notify(self, ids=None):
        if ids:
            act = ACT_UPDATE
        else:
            act = ACT_INIT
            ids = ConfigTrainingMatchReward.INSTANCES.keys()

        doc = MongoTrainingMatch.db(self.server_id).find_one({'_id': self.char_id})

        notify = TrainingMatchNotify()
        notify.act = act
        notify.remained_relive_times = RELIVE_TIMES - doc['relive_times']
        notify.relive_cost = RELIVE_DIAMOND

        for i in ids:
            club = Club.loads(doc['clubs'][i - 1])

            notify_club = notify.clubs.add()
            notify_club.index = i
            notify_club.flag = club.flag
            notify_club.name = club.name
            notify_club.level = club.level
            # TODO
            notify_club.power = 9999

            if i in doc['rewards']:
                notify_club.status = TRAINING_MATCH_CLUB_DONE
                continue

            status = doc['status'].get(str(i), None)
            if status is None:
                notify_club.status = TRAINING_MATCH_CLUB_NOT_OPEN
            elif status == 1:
                notify_club.status = TRAINING_MATCH_CLUB_OPEN
            elif status == 2:
                notify_club.status = TRAINING_MATCH_CLUB_PASS
            else:
                notify_club.status = TRAINING_MATCH_CLUB_FAIL

        MessagePipe(self.char_id).put(msg=notify)
