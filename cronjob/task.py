# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       task
Date Created:   2015-08-03 17:09
Description:

"""

import traceback

import uwsgidecorators
from apps.server.models import Server
from core.task import RandomEvent
from core.mongo import MongoTaskDaily
from cronjob.log import Logger


@uwsgidecorators.cron(0, 0, -1, -1, -1, target="spooler")
def reset_random_event(*args):
    logger = Logger("reset_random_event")
    logger.write("Start")

    try:
        for sid in Server.opened_server_ids():
            RandomEvent.cronjob(sid)

            logger.write("Server {0} Finish".format(sid))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()


@uwsgidecorators.cron(0, 0, -1, -1, -1, target="spooler")
def reset_task_daily(*args):
    logger = Logger("reset_task_daily")
    logger.write("Start")

    try:
        for sid in Server.opened_server_ids():
            MongoTaskDaily.db(sid).drop()

            logger.write("Server {0} Finish".format(sid))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
