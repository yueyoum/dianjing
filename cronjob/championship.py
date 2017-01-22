# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       championship
Date Created:   2016-12-14 10:53
Description:

"""

import traceback
import arrow

import uwsgidecorators

from django.conf import settings
from apps.server.models import Server
from core.championship import (
    APPLY_WEEKDAY,
    APPLY_TIME_RANGE,
    GROUP_MATCH_TIME,
    MATCH_AHEAD_MINUTE,
    LEVEL_MATCH_TIMES_TO_HOUR_MINUTE_TABLE,
    before_apply,
    ChampionshipLevel,
    ChampionshipGroupManager,
)

from utils.functional import make_time_of_today

from cronjob.log import Logger

# 报名前清理，提前启动
_time1 = make_time_of_today(APPLY_TIME_RANGE[0][0], APPLY_TIME_RANGE[0][1])
_time1 = _time1.replace(minutes=-2)


@uwsgidecorators.cron(_time1.minute, _time1.hour, -1, -1, -1, target="spooler")
def champion_before_apply(*args):
    now = arrow.utcnow().to(settings.TIME_ZONE)
    if now.weekday() not in APPLY_WEEKDAY:
        return

    logger = Logger("champion_before_apply")
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            before_apply(sid)
            logger.write("Server {0} Finish.".format(sid))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()


# 分组
# 报名结束后开始
@uwsgidecorators.cron(APPLY_TIME_RANGE[1][1], APPLY_TIME_RANGE[1][0], -1, -1, -1, target="spooler")
def champion_make_group(*args):
    now = arrow.utcnow().to(settings.TIME_ZONE)
    if now.weekday() not in APPLY_WEEKDAY:
        return

    logger = Logger("champion_make_group")
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            club_ids = ChampionshipGroupManager.find_applied_clubs(sid)
            ChampionshipGroupManager.assign_to_groups(sid, club_ids)
            logger.write("Server {0} Finish. Real Club Amount: {0}".format(len(club_ids)))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()


# 小组赛
def champion_group_match(*args):
    now = arrow.utcnow().to(settings.TIME_ZONE)
    if now.weekday() not in APPLY_WEEKDAY:
        return

    logger = Logger("champion_group_match")
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            match_times = ChampionshipGroupManager.start_match(sid)
            logger.write("Server {0} Finish Match {1}".format(sid, match_times))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()


for _h, _m in GROUP_MATCH_TIME:
    _time2 = make_time_of_today(_h, _m)
    _time2 = _time2.replace(minutes=-MATCH_AHEAD_MINUTE)
    uwsgidecorators.cron(_time2.minute, _time2.hour, -1, -1, -1, target="spooler")(champion_group_match)


# XX强赛
def champion_level_match(*args):
    now = arrow.utcnow().to(settings.TIME_ZONE)
    if now.weekday() not in APPLY_WEEKDAY:
        return

    logger = Logger("champion_level_match")
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            lv = ChampionshipLevel(sid).start_match()
            logger.write("Server {0} Finish Level Math {1}".format(sid, lv))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()


for _, (_h, _m) in LEVEL_MATCH_TIMES_TO_HOUR_MINUTE_TABLE.iteritems():
    _time3 = make_time_of_today(_h, _m)
    _time3 = _time3.replace(minutes=-MATCH_AHEAD_MINUTE)
    uwsgidecorators.cron(_time3.minute, _time3.hour, -1, -1, -1, target="spooler")(champion_level_match)
