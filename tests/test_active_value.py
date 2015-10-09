# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       active_value
Date Created:   2015-10-09 17:51
Description:

"""
import random

from dianjing.exception import GameException

from core.mongo import MongoActiveValue
from core.active_value import ActiveValue

from config import ConfigActiveReward, ConfigActiveFunction, ConfigErrorMessage

class TestActiveValue(object):
    def setup(self):
        ActiveValue(1, 1)

    def teardown(self):
        MongoActiveValue.db(1).drop()

    def test_send_notify(self):
        ActiveValue(1, 1).send_value_notify()
        ActiveValue(1, 1).send_function_notify()

    def test_trig(self):
        func = random.choice(ConfigActiveFunction.all_functions())
        config = ConfigActiveFunction.get(func)

        doc = MongoActiveValue.db(1).find_one({'_id': 1})
        assert doc['value'] == 0
        assert func not in doc['funcs']

        ActiveValue(1, 1).trig(func)

        doc = MongoActiveValue.db(1).find_one({'_id': 1})
        assert doc['value'] == config.value
        assert doc['funcs'][func] == 1


    def test_get_reward(self):
        i = random.choice(ConfigActiveReward.INSTANCES.keys())
        config = ConfigActiveReward.get(i)

        MongoActiveValue.db(1).update_one(
            {'_id': 1},
            {'$set': {'value': config.value}}
        )

        ActiveValue(1, 1).get_reward(i)

        doc = MongoActiveValue.db(1).find_one({'_id': 1})
        assert i in doc['rewards']

    def test_get_reward_can_not(self):
        i = random.choice(ConfigActiveReward.INSTANCES.keys())

        try:
            ActiveValue(1, 1).get_reward(i)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("ACTIVE_REWARD_CAN_NOT_GET")
        else:
            raise Exception("can not be here!")
