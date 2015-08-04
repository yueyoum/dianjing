# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_notification
Date Created:   2015-08-04 18:34
Description:

"""

from core.notification import Notification

class TestNotification(object):
    def test_send_notify(self):
        Notification(1, 1).send_notify()

