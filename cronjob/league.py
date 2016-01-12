# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       league
Date Created:   2015-05-18 15:28
Description:

"""

import traceback

import arrow
import uwsgidecorators

from django.conf import settings
from apps.server.models import Server
from cronjob.log import Logger
from core.league.league import LeagueManger
from config.settings import (
    LEAGUE_REFRESH_TIME_ONE,
    LEAGUE_REFRESH_TIME_TWO,
    LEAGUE_REFRESH_TIME_THREE,
    LEAGUE_REFRESH_TIME_FOUR,
    LEAGUE_CHALLENGE_TIMES_REFRESH_TIME,
)

time_one = arrow.get(LEAGUE_REFRESH_TIME_ONE, "HH:mm:ssZ").replace(days=+1).to(settings.TIME_ZONE)
time_two = arrow.get(LEAGUE_REFRESH_TIME_TWO, "HH:mm:ssZ").replace(days=+1).to(settings.TIME_ZONE)
time_three = arrow.get(LEAGUE_REFRESH_TIME_THREE, "HH:mm:ssZ").replace(days=+1).to(settings.TIME_ZONE)
time_four = arrow.get(LEAGUE_REFRESH_TIME_FOUR, "HH:mm:ssZ").replace(days=+1).to(settings.TIME_ZONE)

time_five = arrow.get(LEAGUE_CHALLENGE_TIMES_REFRESH_TIME, "HH:mm:ssZ").replace(days=+1).to(settings.TIME_ZONE)


# 每天刷新联赛挑战次数
@uwsgidecorators.cron(time_five.minute, time_five.hour, -1, -1, -1, target="spooler")
def league_challenge_times_refresh(*args):
    logger = Logger("league_challenge_times_refresh")
    logger.write("Start")

    try:
        server_ids = Server.opened_server_ids()
        for s in server_ids:
            logger.write("server {0} start".format(s))
            LeagueManger.refresh_challenge_times(s)
            logger.write("server {0} finish".format(s))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()


# 每天定时刷新联赛挑战目标
def league_challenge_club_refresh(*args):
    logger = Logger("league_challenge_club_refresh")
    logger.write("Refresh")

    try:
        server_ids = Server.opened_server_ids()
        for s in server_ids:
            logger.write("server {0} start".format(s))
            LeagueManger.timer_refresh(s)
            logger.write("server {0} finish".format(s))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()


uwsgidecorators.cron(time_one.minute, time_one.hour, -1, -1, -1, target="spooler")(league_challenge_club_refresh)
uwsgidecorators.cron(time_two.minute, time_two.hour, -1, -1, -1, target="spooler")(league_challenge_club_refresh)
uwsgidecorators.cron(time_three.minute, time_three.hour, -1, -1, -1, target="spooler")(league_challenge_club_refresh)
uwsgidecorators.cron(time_four.minute, time_four.hour, -1, -1, -1, target="spooler")(league_challenge_club_refresh)
