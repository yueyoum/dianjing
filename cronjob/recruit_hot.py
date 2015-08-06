# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       recruit_hot
Date Created:   2015-08-06 16:44
Description:

"""

import uwsgidecorators

from core.db import MongoDB
from core.mongo import MONGO_COMMON_KEY_RECRUIT_HOT
from core.common import Common

from cronjob.log import Logger

@uwsgidecorators.cron(0, -1, -1, -1, -1, target='mule')
def recruit_hot_reset(*args):
    logger = Logger("recruit_hot_reset")
    logger.write("Start")

    servers = MongoDB.server_ids()
    for s in servers:
        Common.delete(s, MONGO_COMMON_KEY_RECRUIT_HOT)

    logger.write("Done")
    logger.close()
