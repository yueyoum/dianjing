# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       ladder
Date Created:   2015-09-10 18:16
Description:

"""

import traceback
import uwsgidecorators

from core.db import MongoDB
from core.mongo import MongoLadder
from cronjob.log import Logger

from core.ladder import Ladder

@uwsgidecorators.cron(30, 21, -1, -1, -1, target="spooler")
def ladder_send_rank_reward(*args):
    logger = Logger("ladder_rank_reward")
    logger.write("Start")

    try:
        servers = MongoDB.server_ids()
        for s in servers:
            Ladder.send_rank_reward(s)
            logger.write("Server {0} finish".format(s))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()


@uwsgidecorators.cron(0, 0, -1, -1, -1, target="spooler")
def ladder_store_clean_buy_times(*args):
    logger = Logger("ladder_store_clean_buy_times")
    logger.write("Start")

    try:
        for s in MongoDB.server_ids():
            MongoLadder.db(s).update_many(
                {},
                {'$set': {'buy_times': {}}}
            )

            logger.write("Server {0} finish".format(s))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
