# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       business
Date Created:   2015-11-04 10:49
Description:    商务部的定时任务。 赞助，网店

"""

import traceback

import uwsgidecorators
from apps.server.models import Server
from core.training import TrainingShop, TrainingSponsor
from cronjob.log import Logger


@uwsgidecorators.cron(0, 0, -1, -1, -1, target="spooler")
def training_shop_cronjob(*args):
    logger = Logger('training_shop')
    logger.write("Start")

    try:
        for s in Server.opened_server_ids():
            TrainingShop.cronjob(s)
            logger.write("Server {0} finish".format(s))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()


@uwsgidecorators.cron(0, 0, -1, -1, -1, target="spooler")
def training_sponsor_cronjob(*args):
    logger = Logger('training_sponsor')
    logger.write("Start")

    try:
        for s in Server.opened_server_ids():
            TrainingSponsor.cronjob(s)
            logger.write("Server {0} finish".format(s))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
