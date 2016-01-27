# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       ladder
Date Created:   2015-09-10 18:16
Description:

"""

import traceback
import uwsgidecorators

from apps.server.models import Server
from cronjob.log import Logger

from core.ladder import Ladder, LadderStore


@uwsgidecorators.cron(30, 21, -1, -1, -1, target="spooler")
def ladder_send_rank_reward(*args):
    logger = Logger("ladder_rank_reward")
    logger.write("Start")

    try:
        for s in Server.opened_server_ids():
            Ladder.cronjob(s)
            logger.write("Server {0} finish".format(s))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()


@uwsgidecorators.cron(0, 0, -1, -1, -1, target="spooler")
def ladder_store_clean_buy_times(*args):
    logger = Logger("ladder_store_clean_buy_times")
    logger.write("Start")

    try:
        for s in Server.opened_server_ids():
            LadderStore.cronjob(s)
            logger.write("Server {0} finish".format(s))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()


@uwsgidecorators.cron(0, 0, -1, -1, -1, target="spooler")
def ladder_refresh_remained_times(*args):
    logger = Logger("ladder_refresh_remained_times")
    logger.write("Start")

    try:
        for s in Server.opened_server_ids():
            Ladder.cronjob_refresh_remained_times(s)
            logger.write("Server {0} finish".format(s))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
