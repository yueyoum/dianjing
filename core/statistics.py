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

    @property
    def get_gold_statistics(self):
        from apps.statistics.models import Statistics

        now = arrow.utcnow().to(settings.TIME_ZONE)
        end = now.replace(days=1)

        end = arrow.Arrow(end.year, end.month, end.day, hour=0, minute=0, second=0, microsecond=0, tzinfo=end.tzinfo)
        start = end.replace(days=-7)

        days = [start.replace(days=i) for i in range(1, 8)]
        income = [0] * len(days)
        expense = [0] * len(days)

        condition = Q(char_id=self.char_id) & Q(create_at__gte=start.format("YYYY-MM-DD HH:mm:ssZ")) & Q(
            create_at__lte=end.format("YYYY-MM-DD HH:mm:ssZ"))

        for s in Statistics.objects.filter(condition).order_by('create_at'):
            create_at = arrow.get(s.create_at).to(settings.TIME_ZONE)

            # 找到这个记录应该属于哪一天
            for i in range(len(days)):
                if create_at < days[i]:
                    index = i
                    break
            else:
                index = len(days)-1

            if s.club_gold > 0:
                income[index] += s.club_gold
            else:
                expense[index] += abs(s.club_gold)

        return income, expense

    def send_notify(self):
        # 只有 gold 需要notify
        income, expense = self.get_gold_statistics

        notify = FinanceStatisticsNotify()
        notify.income.extend(income)
        notify.expense.extend(expense)

        MessagePipe(self.char_id).put(msg=notify)
