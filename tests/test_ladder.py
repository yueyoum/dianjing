# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_ladder
Date Created:   2015-08-19 11:30
Description:

"""

import random

from dianjing.exception import GameException

from core.db import MongoDB
from core.mongo import MONGO_COMMON_KEY_LADDER_STORE
from core.common import Common
from core.ladder import Ladder, LadderStore
from core.staff import StaffManger
from core.club import Club
from core.training import TrainingBag

from config import ConfigStaff, ConfigErrorMessage



class TestLadder(object):
    def teardown(self):
        MongoDB.get(1).ladder.drop()

        MongoDB.get(1).staff.delete_one({'_id': 1})
        MongoDB.get(1).character.update_one(
            {'_id': 1},
            {'$set': {
                'club.match_staffs': [],
                'club.tibu_staffs': []
            }}
        )

    def test_send_notify(self):
        Ladder(1, 1).send_notify()

    def test_refresh(self):
        Ladder(1, 1).make_refresh()

    def test_match(self):
        staff_ids = ConfigStaff.INSTANCES.keys()
        staff_ids = random.sample(staff_ids, 10)

        sm = StaffManger(1, 1)
        for i in staff_ids:
            sm.add(i)

        Club(1, 1).set_match_staffs(staff_ids)


        ladder = Ladder(1, 1)

        doc = MongoDB.get(1).ladder.find_one({'_id': '1'})
        refreshed = doc['refreshed'].keys()

        target_id = random.choice(refreshed)

        ladder.match(target_id)

    def test_get_top_clubs(self):
        Ladder.get_top_clubs(1)


class TestLadderStore(object):
    def teardown(self):
        MongoDB.get(1).staff.delete_one({'_id': 1})
        Common.delete(1, MONGO_COMMON_KEY_LADDER_STORE)

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

    def test_buy(self):
        l = LadderStore(1, 1)
        t = TrainingBag(1, 1)
        item_id = random.choice(l.items)

        assert t.has_training(item_id) is False
        l.buy(item_id)
        # assert t.has_training(item_id) is True
