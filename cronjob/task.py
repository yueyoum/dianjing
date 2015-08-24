# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       task
Date Created:   2015-08-03 17:09
Description:

"""

import traceback

import uwsgidecorators

from core.db import MongoDB
from core.task import TaskManager, TaskRefresh
from cronjob.log import Logger


@uwsgidecorators.cron(-10, -1, -1, -1, -1, target='spooler')
def task_refresh(*args):
    logger = Logger("task_refresh")
    logger.write("Start")

    try:
        for server_id in MongoDB.server_ids():
            TaskRefresh.cron_job(server_id)
            TaskManager.clean(server_id)
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
