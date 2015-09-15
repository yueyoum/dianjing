# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       task
Date Created:   2015-08-03 17:09
Description:

"""

import traceback

import uwsgidecorators
from apps.server.models import Server
from core.task import TaskManager, TaskRefresh
from cronjob.log import Logger


@uwsgidecorators.cron(-10, -1, -1, -1, -1, target='spooler')
def task_refresh(*args):
    logger = Logger("task_refresh")
    logger.write("Start")

    try:
        for sid in Server.opened_server_ids():
            TaskRefresh.cron_job(sid)
            TaskManager.clean(sid)
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
