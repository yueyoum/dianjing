# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       tower
Date Created:   2016-06-06 18-23
Description:

"""

import traceback

import uwsgidecorators
from apps.server.models import Server
from core.tower import Tower
from cronjob.log import Logger


@uwsgidecorators.cron(0, 0, -1, -1, -1, target="spooler")
def reset_random_event(*args):
    logger = Logger("reset_tower_star")
    logger.write("Start")

    try:
        for sid in Server.opened_server_ids():
            Tower.reset_star(sid)
            logger.write("Server {0} Finish".format(sid))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
