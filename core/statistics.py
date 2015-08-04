# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       statistics
Date Created:   2015-08-04 18:57
Description:

"""

from core.db import MongoDB
from utils.message import MessagePipe

from protomsg.statistics_pb2 import FinanceStatisticsNotify

class FinanceStatistics(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = MongoDB.get(server_id)



    def send_notify(self):
        # TODO real data
        income = [19, 45, 900, 343, 0, 76, 3]
        expense = [90, 23, 11, 98, 34, 300, 0]

        notify = FinanceStatisticsNotify()
        notify.income.extend(income)
        notify.expense.extend(expense)

        MessagePipe(self.char_id).put(msg=notify)

