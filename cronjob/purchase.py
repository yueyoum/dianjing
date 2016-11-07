# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       purchase
Date Created:   2016-08-11 15:58
Description:

"""

import traceback
import uwsgidecorators

from apps.server.models import Server

from cronjob.log import Logger
from core.purchase import Purchase

@uwsgidecorators.cron(0, 0, -1, -1, -1, target='spooler')
def send_yueka_reward(*args):
    logger = Logger("send_yueka_reward")
    logger.write("Start")

    try:
        server_ids = Server.duty_server_ids()
        for s in server_ids:
            amount = Purchase.send_yueka_reward(s)
            logger.write("server {0} done. send amount {1}".format(s, amount))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
