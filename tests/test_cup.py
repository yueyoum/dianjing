# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_cup
Date Created:   2015-08-27 17:11
Description:

"""

from core.db import MongoDB
from core.cup import Cup

class TestCup(object):
    def teardown(self):
        MongoDB.get(1).cup.drop()
        MongoDB.get(1).cup_club.drop()


    def test_all(self):
        Cup.new(1)
        Cup.prepare(1)
        Cup.match(1)

        Cup(1, 1).make_cup_protomsg()
