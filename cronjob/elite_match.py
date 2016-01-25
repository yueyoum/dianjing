# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       elite_match
Date Created:   2015-12-18 18:29
Description:

"""

import traceback
import uwsgidecorators

from apps.server.models import Server
from cronjob.log import Logger

from core.elite_match import EliteMatch


# @uwsgidecorators.cron(0, -1, -1, -1, -1, target='spooler')
# def add_times(*args):
#     logger = Logger("elite_add_times")
#     logger.write("Start")
#
#     try:
#         for s in Server.opened_server_ids():
#             EliteMatch.cronjob_clean_match_times(s)
#             logger.write("Server {0} finish".format(s))
#     except:
#         logger.error(traceback.format_exc())
#     else:
#         logger.write("Done")
#     finally:
#         logger.close()


@uwsgidecorators.cron(0, 0, -1, -1, -1, target='spooler')
def clean_match_times(*args):
    logger = Logger("elite_clean_match_times")
    logger.write("Start")

    try:
        for s in Server.opened_server_ids():
            EliteMatch.cronjob_clean_match_times(s)
            logger.write("Server {0} finish".format(s))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
