# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       functional
Date Created:   2015-08-11 19:00
Description:

"""

import uuid

import arrow

from django.conf import settings

def make_string_id():
    return str(uuid.uuid4())

def get_arrow_time_of_today():
    # 今天的起始时间
    """

    :rtype: arrow.Arrow
    """
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

    return start_day
