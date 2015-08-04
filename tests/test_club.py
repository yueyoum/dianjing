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
from core.db import MongoDB

from config import ConfigPolicy, ConfigErrorMessage

class TestClub(object):
    def reset(self):
        mongo = MongoDB.get(1)
        mongo.character.update_one(
            {'_id': 1},
            {'$set': {
                'club.gold': 0,
                'club.diamond': 0,
                'club.level': 1,
                'club.renown': 0
            }}
        )

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
