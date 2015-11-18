# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       recruit_hot
Date Created:   2015-08-06 16:44
Description:

"""

import uwsgidecorators
from apps.server.models import Server
from core.common import CommonRecruitHot
from core.active_value import ActiveValue
from cronjob.log import Logger

@uwsgidecorators.cron(0, 0, -1, -1, -1, target='spooler')
def recruit_hot_reset(*args):
    logger = Logger("recruit_hot_reset")
    logger.write("Start")

    server_ids = Server.opened_server_ids()
    for s in server_ids:
        CommonRecruitHot.delete(s)

    logger.write("Done")
    logger.close()


@uwsgidecorators.cron(0, 0, -1, -1, -1, target='spooler')
def active_value_reset(*args):
    logger = Logger("active_value_reset")
    logger.write("Start")

    server_ids = Server.opened_server_ids()
    for s in server_ids:
        ActiveValue.cronjob(s)

    logger.write("Done")
    logger.close()
