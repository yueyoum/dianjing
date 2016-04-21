# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       times_log
Date Created:   2016-04-21 15-04
Description:

"""

import uuid
import arrow

from django.conf import settings

from core.mongo import MongoRecordLog

# TODO 定时清理
class RecordLog(object):
    KEY = None
    __slots__ = ['server_id', 'char_id', 'key']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.key = "{0}:{1}".format(self.KEY, self.char_id)

    def record(self, value=1):
        doc = MongoRecordLog.document()
        doc['_id'] = uuid.uuid4()
        doc['key'] = self.key
        doc['timestamp'] = arrow.utcnow().timestamp
        doc['value'] = value

        MongoRecordLog.db(self.server_id).insert_one(doc)

    def count_of_today(self):
        # 今天一共多少次
        now = arrow.utcnow().to(settings.TIME_ZONE)
        start_day = arrow.Arrow(
            year=now.year,
            month=now.month,
            day=now.day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
            tzinfo=now.tzinfo
        )

        end_day = start_day.replace(days=1)
        return self.count(start_at=start_day.timestamp, end_at=end_day.timestamp)

    def count(self, start_at=None, end_at=None):
        # 一共多少次
        condition = [{'key': self.key}]
        if start_at:
            condition.append({'timestamp': {'$gte': start_at}})
        if end_at:
            condition.append({'timestamp': {'$lte': end_at}})

        docs = MongoRecordLog.db(self.server_id).find({'$and': condition}, {'value': 1})

        value = 0
        for d in docs:
            value += d['value']

        return value

    def days(self, start_at, end_at):
        # 一共多少天
        condition = [
            {'key': self.key},
            {'timestamp': {'$gte': start_at}},
            {'timestamp': {'$lte': end_at}},
        ]

        docs = MongoRecordLog.db(self.server_id).find({'$and': condition})

        dates = set()
        for d in docs:
            date = arrow.get(d['timestamp']).to(settings.TIME_ZONE).format("YYYY-MM-DD")
            dates.add(date)

        return len(dates)

# 抽卡次数
class RecordLogStaffRecruitTimes(RecordLog):
    KEY = 'staff_recruit_times'
    __slots__ = []

    def __init__(self, server_id, char_id, tp):
        super(RecordLogStaffRecruitTimes, self).__init__(server_id, char_id)
        self.key = "{0}:{1}".format(self.key, tp)

# 抽卡获得积分
class RecordLogStaffRecruitScore(RecordLog):
    KEY = 'staff_recruit_score'
    __slots__ = []

    def __init__(self, server_id, char_id, tp):
        super(RecordLogStaffRecruitScore, self).__init__(server_id, char_id)
        self.key = "{0}:{1}".format(self.key, tp)

# 抽卡金币免费次数
class RecordLogStaffRecruitGoldFreeTimes(RecordLog):
    KEY = 'staff_recruit_gold_free_times'
    __slots__ = []
