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

from core.value_log import ValueLog
from utils.operation_log import OperationLog

from cronjob.log import Logger


@uwsgidecorators.cron(0, 3, -1, -1, -1, target='spooler')
def clean_statistics(*args):
    logger = Logger("clean_statistics")
    logger.write("Start")

    try:
        num = Statistics.cronjob()
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done. Delete {0}".format(num))
    finally:
        logger.close()


@uwsgidecorators.cron(30, 3, -1, -1, -1, target='spooler')
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


@uwsgidecorators.cron(0, 4, -1, -1, -1, target='spooler')
def clean_value_log(*args):
    logger = Logger('clean_value_log')
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            ValueLog.clean(sid)
            logger.write("Server {0} Done.".format(sid))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()


@uwsgidecorators.cron(30, 4, -1, -1, -1, target='spooler')
def clean_operation_log(*args):
    logger = Logger('clean_operation_log')
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            OperationLog.clean(sid)
            logger.write("Server {0} Done.".format(sid))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()