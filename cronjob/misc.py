# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       recruit_hot
Date Created:   2015-08-06 16:44
Description:

"""
import traceback

import uwsgidecorators
from apps.server.models import Server
from apps.statistics.models import Statistics
from apps.account.models import AccountLoginLog

from core.common import CommonRecruitHot
from core.active_value import ActiveValue
from cronjob.log import Logger


@uwsgidecorators.cron(0, 0, -1, -1, -1, target='spooler')
def recruit_hot_reset(*args):
    logger = Logger("recruit_hot_reset")
    logger.write("Start")

    try:
        server_ids = Server.opened_server_ids()
        for s in server_ids:
            CommonRecruitHot.delete(s)
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()


@uwsgidecorators.cron(0, 0, -1, -1, -1, target='spooler')
def active_value_reset(*args):
    logger = Logger("active_value_reset")
    logger.write("Start")

    try:
        server_ids = Server.opened_server_ids()
        for s in server_ids:
            ActiveValue.cronjob(s)
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()


@uwsgidecorators.cron(10, 4, -1, -1, -1, target='spooler')
def clean_statistics(*args):
    logger = Logger("clean_statistics")
    logger.write("Start")

    try:
        Statistics.cronjob()
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()


@uwsgidecorators.cron(20, 4, -1, -1, -1, target='spooler')
def clean_account_log(*args):
    logger = Logger('clean_account_log')
    logger.write("Start")

    try:
        AccountLoginLog.cronjob()
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
