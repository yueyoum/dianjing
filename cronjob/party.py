# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       party
Date Created:   2016-09-27 15:37
Description:

"""

import traceback

import uwsgidecorators
from apps.server.models import Server

from core.party import Party

from cronjob.log import Logger

@uwsgidecorators.cron(0, 12, -1, -1, -1, target="spooler")
def party_clean_talent_id(*args):
    logger = Logger("party_clean_talent_id")
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            Party.clean_talent_id(sid)
            logger.write("Server {0} Finish".format(sid))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()

