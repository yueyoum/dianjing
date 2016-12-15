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
from core.championship import ChampionshipLevel, ChampionshipGroupManager

from cronjob.log import Logger

# 分组
# @uwsgidecorators.cron(0, 0, -1, -1, -1, target="spooler")
def champion_make_group(*args):
    logger = Logger("champion_make_group")
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            club_ids = ChampionshipGroupManager.find_applied_clubs(sid)
            ChampionshipGroupManager.assign_to_groups(sid, club_ids)
            logger.write("Server {0} Finish. Club Amount: {0}".format(len(club_ids)))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()

# 小组赛
# @uwsgidecorators.cron(0, -1, -1, -1, -1, target="spooler")
def champion_group_match(*args):
    # 注意，提前启动
    now = arrow.utcnow().to(settings.TIME_ZONE)
    if now.hour not in [14,15,16,17,18,19]:
        return

    logger = Logger("champion_group_match")
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            ChampionshipGroupManager.start_match(sid)
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()

# XX强赛
# @uwsgidecorators.cron(-30, -1, -1, -1, -1, target="spooler")
def champion_level_match(*args):
    now = arrow.utcnow().to(settings.TIME_ZONE)
    if now.hour not in []:
        pass


    logger = Logger("champion_level_match")
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            ChampionshipLevel(sid).start_match()
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
