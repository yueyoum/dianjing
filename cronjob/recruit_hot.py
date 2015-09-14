# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       recruit_hot
Date Created:   2015-08-06 16:44
Description:

"""

import uwsgidecorators

from core.db import MongoDB
from core.common import CommonRecruitHot

from cronjob.log import Logger

@uwsgidecorators.cron(0, -1, -1, -1, -1, target='spooler')
def recruit_hot_reset(*args):
    logger = Logger("recruit_hot_reset")
    logger.write("Start")

    servers = MongoDB.server_ids()
    for s in servers:
        CommonRecruitHot.delete(s)

    logger.write("Done")
    logger.close()
