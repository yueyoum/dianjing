# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_club
Date Created:   2015-08-04 15:16
Description:

"""

import random

from dianjing.exception import GameException

from core.club import Club, club_level_up_need_renown
from core.staff import StaffManger
from core.db import MongoDB

from config import ConfigPolicy, ConfigErrorMessage, ConfigStaff

class TestClub(object):
    def reset(self):
        MongoDB.get(1).character.update_one(
            {'_id': 1},
            {'$set': {
                'club.gold': 0,
                'club.diamond': 0,
                'club.level': 1,
                'club.renown': 0,
                'club.match_staffs': [],
                'club.tibu_staffs': []
            }}
        )

        MongoDB.get(1).staff.delete_one({'_id': 1})


    def setUp(self):
        self.reset()

    def tearDown(self):
        self.reset()


    def test_set_policy(self):
        policy = random.choice(ConfigPolicy.INSTANCES.keys())

        club = Club(1, 1)
        club.set_policy(policy)
        assert club.policy == policy

        doc = MongoDB.get(1).character.find_one({'_id': 1}, {'club.policy': 1})
        assert doc['club']['policy'] == policy


    def test_set_policy_not_exists(self):
        def _get_policy():
            while True:
                policy = random.randint(1, 1000)
                if policy not in ConfigPolicy.INSTANCES.keys():
                    return policy

        policy = _get_policy()

        club = Club(1, 1)
        try:
            club.set_policy(policy)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("POLICY_NOT_EXIST")
            doc = MongoDB.get(1).character.find_one({'_id': 1}, {'club.policy': 1})
            assert doc['club']['policy'] != policy
        else:
            raise Exception("can not be here")


    def test_add_gold(self):
        gold = 99
        club = Club(1, 1)
        club.update(gold=gold)

        doc = MongoDB.get(1).character.find_one({'_id': 1}, {'club': 1})
        assert doc['club']['gold'] == gold
        assert club.gold == gold


    def test_level_not_up(self):
        renown = club_level_up_need_renown(1) - 1
        club = Club(1, 1)
        club.update(renown=renown)

        doc = MongoDB.get(1).character.find_one({'_id': 1}, {'club': 1})
        assert doc['club']['level'] == 1
        assert club.level == 1


    def test_level_up_to_two(self):
        renown = club_level_up_need_renown(1) + 1
        club = Club(1, 1)
        club.update(renown=renown)

        doc = MongoDB.get(1).character.find_one({'_id': 1}, {'club': 1})
        assert doc['club']['level'] == 2
        assert club.level == 2

    def test_level_up_to_five(self):
        renown = 0
        for i in range(1, 5):
            renown += club_level_up_need_renown(i)

        renown += 1

        club = Club(1, 1)
        club.update(renown=renown)

        doc = MongoDB.get(1).character.find_one({'_id': 1}, {'club': 1})
        assert doc['club']['level'] == 5
        assert club.level == 5


    def test_set_staffs_not_own(self):
        staff_ids = random.sample(ConfigStaff.INSTANCES.keys(), 10)
        try:
            Club(1, 1).set_match_staffs(staff_ids)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST")
        else:
            raise RuntimeError("can not be here!")


    def test_set_staffs(self):
        staff_ids = random.sample(ConfigStaff.INSTANCES.keys(), 10)
        sm = StaffManger(1, 1)
        for sid in staff_ids:
            sm.add(sid)

        Club(1, 1).set_match_staffs(staff_ids)

        assert len(Club(1, 1).match_staffs) == 5
        assert len(Club(1, 1).tibu_staffs) == 5

        for c in Club(1, 1).match_staffs:
            assert c != 0

        for c in Club(1, 1).tibu_staffs:
            assert c != 0
