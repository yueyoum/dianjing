# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       winning
Date Created:   2017-02-13 15:59
Description:

"""

import traceback

import uwsgidecorators
from apps.server.models import Server
from core.winning import WinningArena, WinningPlunder
from cronjob.log import Logger

@uwsgidecorators.cron(55, 23, -1, -1, -1, target="spooler")
def winning_reset(*args):
    logger = Logger("winning_reset")
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            WinningArena.cronjob(sid)
            WinningPlunder.cronjob(sid)

            logger.write("Server {0} Finish".format(sid))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()

