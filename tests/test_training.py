# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_training
Date Created:   2015-08-05 17:42
Description:

"""

import random

from dianjing.exception import GameException
from core.db import MongoDB

from core.staff import StaffManger
from core.training import Training
from core.club import Club

from config import ConfigTraining, ConfigErrorMessage, ConfigStaff


class TestTraining(object):
    def reset(self):
        MongoDB.get(1).staff.delete_one({'_id': 1})
        MongoDB.get(1).character.update_one(
            {'_id': 1},
            {'$set': {
                'club.gold': 0,
                'club.diamond': 0,
            }}
        )


    def setUp(self):
        self.reset()
        self.config = random.choice(ConfigTraining.INSTANCES.values())


    def tearDown(self):
        self.reset()


    def test_send_notify(self):
        Training(1, 1).send_notify()


    def test_buy(self):
        if self.config.cost_type == 1:
            needs = {'gold': self.config.cost_value}
        else:
            needs = {'diamond': self.config.cost_value}

        Club(1, 1).update(**needs)

        assert Training(1, 1).has_training(self.config.id) is False
        Training(1, 1).buy(self.config.id)
        assert Training(1, 1).has_training(self.config.id) is True

        assert getattr(Club(1, 1), needs.keys()[0]) == 0


    def test_buy_not_exist(self):
        try:
            Training(1, 1).buy(9999)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_NOT_EXIST")
        else:
            raise Exception("can not be here!")


    def test_buy_no_money(self):
        if self.config.cost_type == 1:
            error = "GOLD_NOT_ENOUGH"
        else:
            error = "DIAMOND_NOT_ENOUGH"

        try:
            Training(1, 1).buy(self.config.id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id(error)
        else:
            raise Exception("can not be here!")


    def test_use_no_training(self):
        try:
            Training(1, 1).use(9999, 9999)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_NOT_EXIST")
        else:
            raise Exception("can not be here!")


    def test_use_no_staff(self):
        tid = random.choice(ConfigTraining.INSTANCES.keys())
        MongoDB.get(1).staff.update_one(
            {'_id': 1},
            {'$inc': {'trainings.{0}'.format(tid): 1}},
            upsert=True
        )

        try:
            Training(1, 1).use(9999, tid)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST")
        else:
            raise Exception("can not be here!")


    def test_use(self):
        tid = random.choice(ConfigTraining.INSTANCES.keys())
        MongoDB.get(1).staff.update_one(
            {'_id': 1},
            {'$inc': {'trainings.{0}'.format(tid): 1}},
            upsert=True
        )

        sid = random.choice(ConfigStaff.INSTANCES.keys())
        StaffManger(1, 1).add(sid)

        Training(1, 1).use(sid, tid)

        try:
            StaffManger(1, 1).training_get_reward(sid, 0)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_NOT_FINISHED")
