# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_cup
Date Created:   2015-08-27 17:11
Description:

"""
import random

from core.mongo import MongoCupClub, MongoStaff, MongoCharacter
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

    def test_join_cup(self):
        """
        测试时注意修改报名时间
        """
        Cup(self.server_id, self.char_id).join_cup()

        doc = MongoCharacter.db(self.server_id).find_one({'_id': self.char_id}, {'in_cup': 1})
        assert doc['in_cup']

    def test_match(self):
        pass



