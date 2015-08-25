# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_ladder
Date Created:   2015-08-19 11:30
Description:

"""

import random

from core.db import MongoDB
from core.ladder import Ladder
from core.staff import StaffManger
from core.club import Club

from config import ConfigStaff



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
