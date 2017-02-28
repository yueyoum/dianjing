# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       activity
Date Created:   2017-02-23 17:27
Description:

"""

import traceback

import uwsgidecorators
from apps.server.models import Server
from core.mongo import MongoActivityOnlineTime
from cronjob.log import Logger


@uwsgidecorators.cron(0, 0, -1, -1, -1, target="spooler")
def reset_online_time_activity(*args):
    logger = Logger("reset_online_time_activity")
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            MongoActivityOnlineTime.db(sid).drop()

            logger.write("Server {0} Finish".format(sid))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
