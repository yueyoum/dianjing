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
from core.training import TrainingBag, TrainingStore
from core.club import Club

from config import ConfigTraining, ConfigErrorMessage, ConfigStaff


class TestTrainingStore(object):
    def teardown(self):
        MongoDB.get(1).training_store.drop()

    def test_send_notify(self):
        TrainingStore(1, 1).send_notify()

    def test_refresh(self):
        refresh = TrainingStore(1, 1).refresh()

        doc = MongoDB.get(1).training_store.find_one({'_id': 1})
        assert len(refresh) == len(doc['trainings'])

        for k in refresh.keys():
            assert k in doc['trainings']

    def test_remove(self):
        refresh = TrainingStore(1, 1).refresh()

        tid = random.choice(refresh.keys())

        assert TrainingStore(1, 1).get_training(tid) is not None
        TrainingStore(1, 1).remove(tid)
        assert TrainingStore(1, 1).get_training(tid) is None


class TestTrainingBag(object):
    def reset(self):
        MongoDB.get(1).staff.delete_one({'_id': 1})
        MongoDB.get(1).character.update_one(
            {'_id': 1},
            {'$set': {
                'club.gold': 0,
                'club.diamond': 0,
            }}
        )
        MongoDB.get(1).training_store.drop()


    def setUp(self):
        self.reset()
        refreshed = TrainingStore(1, 1).refresh()
        self.tid = random.choice(refreshed.keys())
        oid = refreshed[self.tid]['oid']
        self.config = ConfigTraining.get(oid)


    def tearDown(self):
        self.reset()


    def test_send_notify(self):
        TrainingBag(1, 1).send_notify()


    def test_buy(self):
        if self.config.cost_type == 1:
            needs = {'gold': self.config.cost_value}
        else:
            needs = {'diamond': self.config.cost_value}

        Club(1, 1).update(**needs)

        assert TrainingBag(1, 1).has_training(self.tid) is False
        TrainingBag(1, 1).buy(self.tid)
        assert TrainingBag(1, 1).has_training(self.tid) is True

        assert getattr(Club(1, 1), needs.keys()[0]) == 0


    def test_buy_not_exist(self):
        try:
            TrainingBag(1, 1).buy(9999)
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
            TrainingBag(1, 1).buy(self.tid)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id(error)
        else:
            raise Exception("can not be here!")


    def test_use_no_training(self):
        try:
            TrainingBag(1, 1).use(9999, 9999)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_NOT_EXIST")
        else:
            raise Exception("can not be here!")


    def test_use_no_staff(self):
        MongoDB.get(1).staff.update_one(
            {'_id': 1},
            {'$set': {'trainings.{0}'.format(self.tid): {'oid': 1}}},
            upsert=True
        )

        try:
            TrainingBag(1, 1).use(9999, self.tid)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST")
        else:
            raise Exception("can not be here!")


    def test_use(self):
        MongoDB.get(1).staff.update_one(
            {'_id': 1},
            {'$set': {'trainings.{0}'.format(self.tid): {'oid': 1}}},
            upsert=True
        )

        sid = random.choice(ConfigStaff.INSTANCES.keys())
        StaffManger(1, 1).add(sid)

        TrainingBag(1, 1).use(sid, self.tid)

        try:
            StaffManger(1, 1).training_get_reward(sid, 0)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_NOT_FINISHED")
