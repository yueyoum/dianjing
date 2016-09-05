# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       plunder
Date Created:   2016-09-02 16:08
Description:

"""

import traceback
import arrow

from django.conf import settings

import uwsgidecorators
from apps.server.models import Server
from core.plunder import Plunder, PLUNDER_AUTO_ADD_HOUR

from cronjob.log import Logger

AUTO_CRON_HOUR = []
for i in PLUNDER_AUTO_ADD_HOUR:
    if i == 0:
        AUTO_CRON_HOUR.append(23)
    else:
        AUTO_CRON_HOUR.append(i-1)


@uwsgidecorators.cron(50, 20, -1, -1, -1, target="spooler")
def plunder_reset_station(*args):
    logger = Logger("plunder_reset_station")
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            Plunder.make_product(sid)
            logger.write("Server {0} Finish".format(sid))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()

@uwsgidecorators.cron(55, -1, -1, -1, -1, target="spooler")
def plunder_auto_add_times(*args):
    now = arrow.utcnow().to(settings.TIME_ZONE)
    if now.hour not in AUTO_CRON_HOUR:
        return

    logger = Logger("plunder_auto_add_times")
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            Plunder.auto_add_plunder_times(sid)
            logger.write("Server {0} Finish".format(sid))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
