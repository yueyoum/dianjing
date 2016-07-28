# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       territory
Date Created:   2016-06-14 17-50
Description:

"""


import traceback

import uwsgidecorators
from apps.server.models import Server
from core.territory import Territory
from cronjob.log import Logger


@uwsgidecorators.cron(0, -1, -1, -1, -1, target="spooler")
def territory_auto_increase_product(*args):
    logger = Logger("territory_auto_increase_product")
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            Territory.auto_increase_product(sid)
            logger.write("Server {0} Finish".format(sid))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
