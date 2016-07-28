# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       arena
Date Created:   2016-06-03 09-40
Description:

"""


import traceback

import uwsgidecorators
from apps.server.models import Server
from core.arena import Arena
from cronjob.log import Logger


@uwsgidecorators.cron(0, 0, -1, -1, -1, target="spooler")
def send_rank_reward(*args):
    logger = Logger("arena_send_rank_reward")
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            Arena.send_rank_reward(sid)
            logger.write("Server {0} Finish".format(sid))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
