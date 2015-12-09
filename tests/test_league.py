# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_league
Date Created:   2015-08-06 15:23
Description:

"""
import time
import random

from core.db import MongoDB
from core.mongo import MongoStaff, MongoCharacter

from core.staff import StaffManger
from core.club import Club
from core.league import League, LeagueGame

from config import ConfigStaff


class TestLeague(object):
    @classmethod
    def setup_class(cls):
        MongoCharacter.db(1).update_one(
            {'_id': 1},
            {'$set': {'club.level': 10}}
        )

        doc = MongoStaff.db(1).find_one({'_id': 1}, {'staffs': 1})
        staff_ids = random.sample(ConfigStaff.INSTANCES.keys(), 15)
        for i in staff_ids:
            if str(i) not in doc['staffs']:
                StaffManger(1, 1).add(i)

        match_staff_ids = []
        for k in doc['staffs'].keys():
            match_staff_ids.append(int(k))

        for staff_id in staff_ids:
            if staff_id not in match_staff_ids:
                match_staff_ids.append(staff_id)

        Club(1, 1).set_match_staffs(random.sample(match_staff_ids, 10))

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
        start = time.clock()
        for i in range(1, 1000 + 1):
            LeagueGame.start_match(1)
        print time.clock() - start

    def test_get_statistics(self):
        doc = MongoDB.get(1).character.find_one({'_id': 1}, {'league_group': 1})
        group_id = doc['league_group']

        group_doc = MongoDB.get(1).league_group.find_one({'_id': group_id})

        for i in group_doc['clubs'].keys():
            League(1, 1).get_statistics(i)

