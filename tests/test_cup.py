# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_cup
Date Created:   2015-08-27 17:11
Description:

"""
import random

from core.mongo import MongoCupClub, MongoStaff
from core.character import Character
from core.cup import Cup

from config.staff import ConfigStaff


class TestCup(object):
    def __init__(self):
        self.server_id = 1
        self.char_id = 1

    def setup(self):
        pass

    def teardown(self):
        pass

    def test_match(self):
        Character.create(self.server_id, self.char_id+1, 'two', 'club_two', 1)
        MongoCupClub.db(self.server_id).update_one(
            {'_id': str(self.char_id+1)},
            {'$set': {}}
        )

        club_one = MongoCupClub.db(self.server_id).find_one({'_id': str(self.char_id)})
        club_two = MongoCupClub.db(self.server_id).find_one({'_id': str(self.char_id+1)})



