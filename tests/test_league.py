# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_league
Date Created:   2015-08-06 15:23
Description:

"""
import random

from core.db import MongoDB

from core.staff import StaffManger
from core.club import Club
from core.league import League, LeagueGame

from config import ConfigStaff


class TestLeague(object):
    @classmethod
    def setup_class(cls):
        staff_ids = random.sample(ConfigStaff.INSTANCES.keys(), 10)
        for i in staff_ids:
            StaffManger(1, 1).add(i)

        Club(1, 1).set_match_staffs(staff_ids)

        LeagueGame.new(1)


    @classmethod
    def teardown_class(cls):
        LeagueGame.clean(1)

        MongoDB.get(1).staff.delete_one({'_id': 1})
        MongoDB.get(1).character.update_one(
            {'_id': 1},
            {'$set': {
                'club.match_staffs': [],
                'club.tibu_staffs': []
            }}
        )


    def test_send_notify(self):
        League(1, 1).send_notify()

    def test_match(self):
        LeagueGame.start_match(1)

    def test_get_statistics(self):
        doc = MongoDB.get(1).character.find_one({'_id': 1}, {'league_group': 1})
        group_id = doc['league_group']

        group_doc = MongoDB.get(1).league_group.find_one({'_id': group_id})

        for i in group_doc['clubs'].keys():
            League(1, 1).get_statistics(i)

