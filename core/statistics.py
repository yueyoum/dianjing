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

from core.signals import task_condition_trig_signal

from utils.message import MessagePipe
from utils.functional import get_start_time_of_today

from protomsg.statistics_pb2 import FinanceStatisticsNotify


class FinanceStatistics(object):
    __slots__ = ['server_id', 'char_id']

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

        condition_name = 'core.statistics.{0}'.format(self.__class__.__name__)
        task_condition_trig_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            condition_name=condition_name
        )

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
                index = len(days) - 1

            if s.club_gold > 0:
                income[index] += s.club_gold
            else:
                expense[index] += abs(s.club_gold)

        return income, expense

    def count_of_today(self):
        today = get_start_time_of_today()
        tomorrow = today.replace(days=1)
        return self.count(start_at=today.timestamp, end_at=tomorrow.timestamp)

    def count(self, start_at=None, end_at=None):
        from apps.statistics.models import Statistics

        condition = Q(char_id=self.char_id)

        if start_at:
            condition & Q(create_at__gte=arrow.get(start_at).format("YYYY-MM-DD HH:mm:ssZ"))
        if end_at:
            condition & Q(create_at__lte=arrow.get(end_at).format("YYYY-MM-DD HH:mm:ssZ"))

        value = 0
        for s in Statistics.objects.filter(condition):
            value += self._count_value_filter(s)

        return value

    def _count_value_filter(self, obj):
        raise NotImplementedError()

    def send_notify(self):
        # 只有 gold 需要notify
        income, expense = self.get_gold_statistics()

        notify = FinanceStatisticsNotify()
        notify.income.extend(income)
        notify.expense.extend(expense)

        MessagePipe(self.char_id).put(msg=notify)


# 金币花费
class GoldCostStatistics(FinanceStatistics):
    __slots__ = []

    def _count_value_filter(self, obj):
        if obj.club_gold < 0:
            return -obj.club_gold

        return 0


# 金币获得
class GoldGotStatistics(FinanceStatistics):
    __slots__ = []

    def _count_value_filter(self, obj):
        if obj.club_gold > 0:
            return obj.club_gold

        return 0


# 钻石花费
class DiamondCostStatistics(FinanceStatistics):
    __slots__ = []

    def _count_value_filter(self, obj):
        if obj.club_diamond < 0:
            return -obj.club_diamond

        return 0


# 钻石获得
class DiamondGotStatistics(FinanceStatistics):
    __slots__ = []

    def _count_value_filter(self, obj):
        if obj.club_diamond > 0:
            return obj.club_diamond

        return 0
