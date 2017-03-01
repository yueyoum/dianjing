# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       getui
Date Created:   2017-03-01 16:35
Description:

"""

import traceback
import arrow

from django.conf import settings

import uwsgidecorators
from utils.push_notification import GeTui
from cronjob.log import Logger


@uwsgidecorators.cron(0, -1, -1, -1, -1, target="spooler")
def getui_energy(*args):
    now = arrow.utcnow().to(settings.TIME_ZONE)
    if now.hour not in [11,12,13,17,18,19,20]:
        return

    logger = Logger("getui_energy")
    logger.write("Start")

    try:
        count = GeTui.job_of_energy_notification()
        logger.write("Done. count: {0}".format(count))
    except:
        logger.error(traceback.format_exc())
    finally:
        logger.close()


@uwsgidecorators.cron(0, 12, -1, -1, -1, target="spooler")
def getui_login(*args):
    logger = Logger("getui_login")
    logger.write("Start")

    try:
        count = GeTui.job_of_login_notification()
        logger.write("Done. count: {0}".format(count))
    except:
        logger.error(traceback.format_exc())
    finally:
        logger.close()
