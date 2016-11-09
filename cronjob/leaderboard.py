# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       leaderboard
Date Created:   2016-08-16 16:41
Description:

"""

import traceback

import uwsgidecorators
from apps.server.models import Server
from core.leaderboard import ClubLeaderBoard

from cronjob.log import Logger

@uwsgidecorators.cron(0, -2, -1, -1, -1, target='spooler')
def generate_club_leaderboard(*args):
    logger = Logger('generate_club_leaderboard')
    logger.write('Start')

    try:
        for sid in Server.duty_server_ids():
            ClubLeaderBoard.generate(sid)
            logger.write("Server {0} Finish".format(sid))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()