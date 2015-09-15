# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       statistics
Date Created:   2015-08-04 18:57
Description:

"""
import arrow

from django.conf import settings
from django.db.models import Q

from utils.message import MessagePipe

from protomsg.statistics_pb2 import FinanceStatisticsNotify


class FinanceStatistics(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def add_log(self, gold=0, diamond=0, message=""):
        from apps.statistics.models import Statistics

        if settings.TEST:
            return

        Statistics.objects.create(
            server_id=self.server_id,
            char_id=self.char_id,
            club_gold=gold,
            club_diamond=diamond,
            message=message
        )

        self.send_notify()

    def get_gold_statistics(self):
        from apps.statistics.models import Statistics

        now = arrow.utcnow().to(settings.TIME_ZONE)
        now = arrow.Arrow(now.year, now.month, now.day, hour=0, minute=0, second=0, tzinfo=now.tzinfo)
        weekday = now.weekday()
        monday = now.replace(days=-weekday)
        next_monday = monday.replace(days=7)

        income = {i: 0 for i in range(0, 7)}
        expense = {i: 0 for i in range(0, 7)}

        condition = Q(create_at__gte=monday.format("YYYY-MM-DD HH:mm:ssZ")) & Q(
            create_at__lte=next_monday.format("YYYY-MM-DD HH:mm:ssZ"))
        for s in Statistics.objects.filter(condition):
            create_at_weekday = arrow.get(s.create_at).to(settings.TIME_ZONE).weekday()
            if s.club_gold > 0:
                income[create_at_weekday] = income.get(create_at_weekday, 0) + s.club_gold
            else:
                expense[create_at_weekday] = expense.get(create_at_weekday, 0) + abs(s.club_gold)

        income = income.items()
        expense = expense.items()

        income.sort(key=lambda item: item[0])
        expense.sort(key=lambda item: item[0])

        income_values = [i for _, i in income]
        expense_values = [i for _, i in expense]

        return income_values, expense_values

    def send_notify(self):
        # 只有 gold 需要notify
        income_values, expense_values = self.get_gold_statistics()

        notify = FinanceStatisticsNotify()
        notify.income.extend(income_values)
        notify.expense.extend(expense_values)

        MessagePipe(self.char_id).put(msg=notify)
