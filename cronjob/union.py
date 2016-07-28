# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       union
Date Created:   2016-07-28 10:50
Description:

"""
import json
import traceback

import uwsgidecorators
from apps.server.models import Server
from core.mongo import MongoUnionMember

from core.union import UnionOwner
from cronjob.log import Logger

@uwsgidecorators.cron(0, 0, -1, -1, -1, target="spooler")
def union_reset_today_contribution(*args):
    logger = Logger("union_reset_today_contribution")
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            MongoUnionMember.db(sid).update_many(
                {},
                {'$set': {
                    'today_contribution': 0
                }}
            )

            logger.write("Server {0} Finish".format(sid))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()

@uwsgidecorators.cron(10, 0, -1, -1, -1, target="spooler")
def union_auto_transfer(*args):
    logger = Logger("union_auto_transfer")
    logger.write("Start")

    try:
        for sid in Server.duty_server_ids():
            result = UnionOwner.try_auto_transfer(sid)
            logger.write("Server {0} Finish".format(sid))
            logger.write(json.dumps(result))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
