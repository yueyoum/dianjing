# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_notification
Date Created:   2015-08-04 18:34
Description:

"""
from dianjing.exception import GameException

from core.db import MongoDB
from core.notification import Notification

from config import ConfigErrorMessage

class TestNotification(object):
    def setup(self):
        n = Notification(1, 1)
        self.noti_id = n.add_league_notification(True, "t", 1, 1, 1)

    def teardown(self):
        MongoDB.get(1).notification.delete_one({'_id': 1})


    def test_send_notify(self):
        Notification(1, 1).send_notify()


    def test_open_not_exist(self):
        try:
            Notification(1, 1).open("xxxxx")
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("NOTIFICATION_NOT_EXIST")
        else:
            raise Exception("can not be here!")


    def test_open(self):
        Notification(1, 1).open(self.noti_id)


    def test_delte_not_exist(self):
        try:
            Notification(1, 1).delete("xxxxx")
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("NOTIFICATION_NOT_EXIST")
        else:
            raise Exception("can not be here!")


    def test_delete(self):
        assert Notification(1, 1).has_notification(self.noti_id) is True
        Notification(1, 1).delete(self.noti_id)
        assert Notification(1, 1).has_notification(self.noti_id) is False

