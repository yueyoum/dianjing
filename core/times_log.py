# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       times_log
Date Created:   2016-04-21 15-04
Description:

"""

import arrow

from core.mongo import MongoTimesLog
from utils.functional import make_string_id, get_arrow_time_of_today


# TODO 定时清理
class TimesLog(object):
    KEY = None
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def make_key(self, sub_id=None):
        # sub_id 是给大类用的， 比如关卡ID
        if not sub_id:
            return "{0}:{1}".format(self.KEY, self.char_id)
        return "{0}:{1}:{2}".format(self.KEY, self.char_id, sub_id)

    def record(self, sub_id=None, value=1):
        doc = MongoTimesLog.document()
        doc['_id'] = make_string_id()
        doc['key'] = self.make_key(sub_id=sub_id)
        doc['timestamp'] = arrow.utcnow().timestamp
        doc['value'] = value

        MongoTimesLog.db(self.server_id).insert_one(doc)

    def count_of_today(self, sub_id=None):
        # 今天多少次
        today = get_arrow_time_of_today()
        tomorrow = today.replace(days=1)
        return self.count(sub_id=sub_id, start_at=today.timestamp, end_at=tomorrow.timestamp)

    def count(self, sub_id=None, start_at=None, end_at=None):
        # 一共多少次
        condition = [{'key': self.make_key(sub_id=sub_id)}]
        if start_at:
            condition.append({'timestamp': {'$gte': start_at}})
        if end_at:
            condition.append({'timestamp': {'$lte': end_at}})

        docs = MongoTimesLog.db(self.server_id).find({'$and': condition}, {'value': 1})

        value = 0
        for d in docs:
            value += d['value']

        return value


class CategoryTimesLog(TimesLog):
    __slots__ = []
    def batch_count_of_today(self):
        """

        :rtype: dict[str, int]
        """
        today = get_arrow_time_of_today()
        tomorrow = today.replace(days=1)
        return self.batch_count(start_at=today.timestamp, end_at=tomorrow.timestamp)

    def batch_count(self, start_at=None, end_at=None):
        """

        :rtype: dict[str, int]
        """
        key_pattern = '^{0}:'.format(self.make_key())
        condition = [{'key': {'$regex': key_pattern}}]

        if start_at:
            condition.append({'timestamp': {'$gte': start_at}})
        if end_at:
            condition.append({'timestamp': {'$lte': end_at}})

        docs = MongoTimesLog.db(self.server_id).find({'$and': condition})
        counts = {}
        for d in docs:
            _, _id = d['key'].rsplit(':', 1)
            if _id in counts:
                counts[_id] += d['value']
            else:
                counts[_id] = d['value']

        return counts


# 抽卡次数
class TimesLogStaffRecruitTimes(CategoryTimesLog):
    KEY = 'staff_recruit_times'
    __slots__ = []

# 抽卡获得积分
class TimesLogStaffRecruitScore(CategoryTimesLog):
    KEY = 'staff_recruit_score'
    __slots__ = []

# 抽卡金币免费次数
class TimesLogStaffRecruitGoldFreeTimes(TimesLog):
    KEY = 'staff_recruit_gold_free_times'
    __slots__ = []


# 挑战赛关卡次数
class TimesLogChallengeMatchTimes(CategoryTimesLog):
    KEY = 'challenge_match'
    __slots__ = []


class TimesLogDungeonMatchTimes(TimesLog):
    KEY = 'dungeon_match'
    __slots__ = []
