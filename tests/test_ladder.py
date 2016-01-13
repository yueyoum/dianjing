# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_ladder
Date Created:   2015-08-19 11:30
Description:

"""

import random

from dianjing.exception import GameException

from core.mongo import MongoLadder
from core.common import CommonLadderStore
from core.ladder import Ladder, LadderStore
from core.staff import StaffManger
from core.club import Club

from config import ConfigStaff, ConfigErrorMessage, ConfigLadderScoreStore


def match_report():
    pass


class TestLadder(object):
    def setUp(self):
        self.server_id = 1
        self.char_id = 1
        Ladder(self.server_id, self.char_id)

    def teardown(self):
        MongoLadder.db(self.server_id).drop()

    def test_send_notify(self):
        Ladder(self.server_id, self.char_id).send_notify()

    def test_refresh(self):
        Ladder(self.server_id, self.char_id).make_refresh()
        doc = MongoLadder.db(self.server_id).find_one({'_id': str(self.char_id)})
        if doc['order'] > 6:
            for k, v in doc['refreshed'].iteritems():
                assert doc['order'] > v
        else:
            for k, v in doc['refreshed'].iteritems():
                assert v <= 6

    def test_match(self):
        ladder = Ladder(self.server_id, self.char_id)

        doc = MongoLadder.db(self.server_id).find_one({'_id': str(self.char_id)})
        refreshed = doc['refreshed'].keys()

        target_id = random.choice(refreshed)

        ladder.match(target_id)

    def test_get_top_clubs(self):
        Ladder.get_top_clubs(self.server_id)

    def report_match(self):
        ladder = Ladder(self.server_id, self.char_id)

        doc = MongoLadder.db(self.server_id).find_one({'_id': str(self.char_id)})
        refreshed = doc['refreshed'].keys()

        target_id = random.choice(refreshed)

        msg = ladder.match(target_id)
        video = ""
        ladder.match_report(video, msg.key, str(self.char_id), "")


class TestLadderStore(object):
    def teardown(self):
        MongoDB.get(1).staff.delete_one({'_id': 1})
        MongoDB.get(1).ladder.drop()
        CommonLadderStore.delete(1)

    def test_send_notify(self):
        LadderStore(1, 1).send_notify()

    def test_buy_not_exist(self):
        l = LadderStore(1, 1)
        try:
            l.buy(9999999999)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("LADDER_STORE_ITEM_NOT_EXIST")
        else:
            raise Exception("can not be here!")

    def test_buy_score_not_enough(self):
        l = LadderStore(1, 1)
        item_id = random.choice(l.items)

        try:
            l.buy(item_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("LADDER_SCORE_NOT_ENOUGH")
        else:
            raise Exception("can not be here")

    def test_buy(self):
        l = LadderStore(1, 1)
        item_id = random.choice(l.items)

        config = ConfigLadderScoreStore.get(item_id)

        MongoLadder.db(1).update_one(
            {'_id': '1'},
            {'$set': {'score': config.score}}
        )

        l.buy(item_id)

        doc = MongoLadder.db(1).find_one({'_id': '1'})
        assert doc['score'] == 0

