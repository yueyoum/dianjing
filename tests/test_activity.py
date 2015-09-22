# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_activity
Date Created:   2015-09-22 11:27
Description:

"""
from dianjing.exception import GameException

from core.mongo import MongoActivity
from core.activity import ActivityLoginReward
from config import ConfigErrorMessage, ConfigLoginReward

class TestLoginReward(object):
    def teardown(self):
        MongoActivity.db(1).drop()


    def test_send_notify(self):
        ActivityLoginReward(1, 1).send_notify()

    def test_get_reward(self):
        try:
            ActivityLoginReward(1, 1).get_reward(10)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("LOGIN_REWARD_NOT_TO_TIME")
        else:
            raise Exception("can not be here!")
