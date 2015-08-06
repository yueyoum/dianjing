# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_challenge
Date Created:   2015-08-06 11:06
Description:

"""

import random

from dianjing.exception import GameException

from core.db import MongoDB
from core.staff import StaffManger
from core.club import Club
from core.challenge import Challenge

from config import ConfigErrorMessage, ConfigChallengeMatch, ConfigStaff


class TestChallenge(object):
    def reset(self):
        MongoDB.get(1).character.update_one(
            {'_id': 1},
            {'$set': {
                'challenge_id': ConfigChallengeMatch.FIRST_ID,
                'club.match_staffs': [],
                'club.tibu_staffs': []
            }}
        )

        MongoDB.get(1).staff.delete_one({'_id': 1})


    def setUp(self):
        self.reset()


    def tearDown(self):
        self.reset()


    def test_send_notify(self):
        Challenge(1, 1).send_notify()


    def test_match_staff_not_ready(self):
        try:
            Challenge(1, 1).start()
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("MATCH_STAFF_NOT_READY")
        else:
            raise Exception("can not be here!")


    def test_match_all_finished(self):
        MongoDB.get(1).character.update_one(
            {'_id': 1},
            {'$set': {'challenge_id': 0}}
        )

        try:
            Challenge(1, 1).start()
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("CHALLENGE_ALL_FINISHED")
        else:
            raise Exception("can not be here!")


    def test_match(self):
        staff_ids = ConfigStaff.INSTANCES.keys()
        staff_ids = random.sample(staff_ids, 10)

        sm = StaffManger(1, 1)
        for i in staff_ids:
            sm.add(i)

        Club(1, 1).set_match_staffs(staff_ids)

        Challenge(1, 1).start()
        
