# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       log
Date Created:   2015-05-18 15:16
Description:

"""

import os
import arrow

from django.conf import settings
from django.core.mail import mail_admins


class Logger(object):
    def __init__(self, name):
        """

        :type name: str
        """

        if not name.endswith(".log"):
            name += ".log"

        self.name = name
        self.f = open(os.path.join(settings.LOG_PATH, self.name), 'a')
        print "==== CRON START  {0} [{1}] ====".format(self.now, self.name)

    @property
    def now(self):
        return arrow.utcnow().to(settings.TIME_ZONE).format("YYYY-MM-DD HH:mm:ss")

    def write(self, text):
        self.f.write("{0} {1}\n".format(self.now, text))

    def error(self, text):
        self.write("==== ERROR ====")
        self.write(text)
        self.write("==== ===== ====")

        mail_title = "CRON ERROR: {0}".format(self.name)
        mail_admins(mail_title, text)

    def close(self):
        self.f.close()
        print "==== CRON FINISH {0} [{1}] ====".format(self.now, self.name)
