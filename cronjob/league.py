# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       league
Date Created:   2015-05-18 15:28
Description:

"""

import arrow
import uwsgidecorators

from django.conf import settings

from cronjob.log import Logger
from apps.server.models import Server

from core.league import LeagueGame

from config.settings import LEAGUE_START_TIME_ONE, LEAGUE_START_TIME_TWO

time_one = arrow.get(LEAGUE_START_TIME_ONE, "HH:mm:ssZ").to(settings.TIME_ZONE)
time_two = arrow.get(LEAGUE_START_TIME_TWO, "HH:mm:ssZ").to(settings.TIME_ZONE)

# 每周创建新的联赛
@uwsgidecorators.cron(0, 0, -1, -1, 1, target="mule")
def league_new(*args):
    logger = Logger("league_new")

    servers = Server.opened_servers()
    for s in servers:
        logger.write("server {0} start".format(s.id))
        LeagueGame.new(s.id)
        logger.write("server {0} finish".format(s.id))

    logger.write("done")
    logger.close()


# 每天定时开启的比赛
def league_match(*args):
    logger = Logger("league_battle")

    servers = Server.opened_servers()
    for s in servers:
        logger.write("server {0} start".format(s.id))
        LeagueGame.start_match(s.id)
        logger.write("server {0} finish".format(s.id))

    logger.write("done")
    logger.close()


uwsgidecorators.cron(time_one.minute, time_one.hour, -1, -1, -1, target="mule")(league_match)
uwsgidecorators.cron(time_two.minute, time_two.hour, -1, -1, -1, target="mule")(league_match)
