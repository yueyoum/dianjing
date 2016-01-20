# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       challenge
Date Created:   2016-01-13 11:28
Description:

"""

import traceback
import uwsgidecorators

from apps.server.models import Server
from cronjob.log import Logger

from core.challenge import Challenge


@uwsgidecorators.cron(0, 0, -1, -1, -1, target='spooler')
def clean_match_times(*args):
    logger = Logger("challenge_clean_match_times")
    logger.write("Start")

    try:
        for s in Server.opened_server_ids():
            Challenge.cronjob_refresh_times(s)
            logger.write("Server {0} finish".format(s))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()


@uwsgidecorators.cron(30, -1, -1, -1, -1, target='spooler')
def energy_energize(*args):
    logger = Logger("character energize")
    logger.write("Start")

    try:
        for s in Server.opened_server_ids():
            Challenge.cronjob_energize(s)
            logger.write("Server {0} finish".format(s))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
