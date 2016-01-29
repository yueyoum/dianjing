# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training_match
Date Created:   2016-01-29 15-12
Description:

"""

import traceback
import uwsgidecorators

from apps.server.models import Server
from cronjob.log import Logger

from core.training_match import TrainingMatchStore

@uwsgidecorators.cron(0, 0, -1, -1, -1, target="spooler")
def training_match_store_reset(*args):
    logger = Logger("training_match_store_reset")
    logger.write("Start")

    try:
        for s in Server.opened_server_ids():
            TrainingMatchStore.cronjob(s)
            logger.write("Server {0} finish".format(s))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
