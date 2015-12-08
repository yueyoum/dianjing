# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_statistics
Date Created:   2015-08-04 19:01
Description:

"""

from core.statistics import FinanceStatistics


class TestFinanceStatistics(object):
    def __init__(self):
        self.server = 1
        self.char_id = 1

    def setup(self):
        pass

    def teardown(self):
        pass

    def test_send_notify(self):
        FinanceStatistics(self.server, self.char_id).send_notify()
