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
def tower_send_reward_and_reset_star(*args):
    logger = Logger("tower_send_reward_and_reset_star")
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            Tower.send_rank_reward_and_reset_star(sid)
            logger.write("Server {0} Finish".format(sid))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
