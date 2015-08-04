# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_statistics
Date Created:   2015-08-04 19:01
Description:

"""

from core.statistics import FinanceStatistics

class TestFinanceStatistics(object):
    def test_send_notify(self):
        FinanceStatistics(1, 1).send_notify()
