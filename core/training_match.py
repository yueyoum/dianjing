# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training_match
Date Created:   2015-12-08 16:16
Description:    训练赛

"""

import random
import arrow

from dianjing.exception import GameException

from core.mongo import MongoCharacter, MongoTrainingMatch

from core.club import Club
from core.package import Drop
from core.resource import Resource
from core.match import ClubMatch
from core.staff import StaffManger

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
        char_docs = MongoCharacter.db(self.server_id).find(condition, {'club.level': 1}).sort('club.level', 1).limit(
            100)

        if char_docs.count() < MAX_MATCH_CLUB:
            for doc in char_docs:
                clubs.append(Club(self.server_id, doc['_id']))

            need_amount = MAX_MATCH_CLUB - len(clubs)
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
        doc['status'] = {'0': TRAINING_MATCH_CLUB_OPEN}
        doc['clubs'] = [c.dumps() for c in clubs]

        MongoTrainingMatch.db(self.server_id).insert_one(doc)

    def add_score(self, score):
        MongoTrainingMatch.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {'score': score}}
        )

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
        return str(arrow.utcnow().timestamp) + ',' + str(index) + ',' + str(self.char_id) + ',' + str(target_id)

    def get_training_match_data(self):
        return MongoTrainingMatch.db(self.server_id).find_one({'_id': self.char_id})

    def match_report(self, is_win, key, result):
        timestamp, index, club_one, club_two = str(key).split(',')

        tmp_drop = None
        updater = {}
        updated_ids = []

        if is_win:
            index = int(index)
            updated_ids = [index]
            if not ConfigTrainingMatchReward.get(index):
                raise GameException(ConfigErrorMessage.get_error_id("TRAINING_MATCH_NOT_EXIST"))

            reward_config = ConfigTrainingMatchReward.get(index)
            tmp_drop = Drop.generate(reward_config.reward)
            tmp_drop.training_match_score = reward_config.score

            message = "Training Match {0} drop".format(index)
            Resource(self.server_id, self.char_id).save_drop(tmp_drop, message=message)

            updater['status.{0}'.format(index)] = TRAINING_MATCH_CLUB_PASS

            if index < MAX_MATCH_CLUB_INDEX:
                next_index = index + 1
                updated_ids.append(next_index)
                updater['status.{0}'.format(next_index)] = TRAINING_MATCH_CLUB_OPEN
        else:
            updater['status.{0}'.format(index)] = TRAINING_MATCH_CLUB_FAIL

        MongoTrainingMatch.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_notify(ids=updated_ids)

        if tmp_drop:
            return tmp_drop.make_protomsg()

    def get_match_detail(self, index):
        doc = self.get_training_match_data()
        staff_ids = Club.loads(doc['clubs'][index]).match_staffs
        return StaffManger(self.server_id, self.char_id).get_staff_by_ids(staff_ids)

    def send_notify(self, ids=None):
        if ids:
            act = ACT_UPDATE
        else:
            act = ACT_INIT
            ids = [i-1 for i in ConfigTrainingMatchReward.INSTANCES.keys()]

        doc = self.get_training_match_data()

        notify = TrainingMatchNotify()
        notify.act = act
        notify.remained_relive_times = MAX_RELIVE_TIMES - doc['relive_times']
        notify.relive_cost = RELIVE_COST_DIAMOND

        for i in ids:
            club = Club.loads(doc['clubs'][i])

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
            else:
                notify_club.status = status

        MessagePipe(self.char_id).put(msg=notify)
