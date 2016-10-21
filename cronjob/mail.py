# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       mail
Date Created:   2015-09-09 15:21
Description:

"""

import traceback
import uwsgidecorators

from django.conf import settings
from apps.server.models import Server
from apps.history_record.models import MailHistoryRecord

from cronjob.log import Logger
from core.mail import get_mail_clean_time
from core.mail import MailManager, AdminMailManager

clean_time = get_mail_clean_time().to(settings.TIME_ZONE)

@uwsgidecorators.cron(-10, 0, 0, 0, 0, target="spooler")
def send_gm_mail(*args):
    logger = Logger("send_gm_mail")
    logger.write("Start")

    gm = AdminMailManager()
    gm.fetch()

    logger.write("Send ids: {0}".format(gm.send_ids))

    try:
        gm.start_send()
    except:
        logger.write("Done ids: {0}".format(gm.done_ids))
        logger.error(traceback.format_exc())
    else:
        logger.write("Done ids: {0}".format(gm.done_ids))
        logger.write("Done")
    finally:
        logger.close()


@uwsgidecorators.cron(0, clean_time.hour, -1, -1, -1, target="spooler")
def clean_mail(*args):
    logger = Logger("clean_mail")
    logger.write("Start")

    try:
        server_ids = Server.duty_server_ids()
        for s in server_ids:
            cleaned_amount = MailManager.cronjob(s)
            logger.write("server {0} cleaned amount {1}".format(s, cleaned_amount))
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()


@uwsgidecorators.cron(30, 2, -1, -1, -1, target="spooler")
def clean_mail_history(*args):
    logger = Logger("clean_mail_history")
    logger.write("Start")

    try:
        MailHistoryRecord.cronjob()
    except:
        logger.error(traceback.format_exc())
    else:
        logger.write("Done")
    finally:
        logger.close()
