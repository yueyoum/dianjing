# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       test_shop
Date Created:   2015-12-01 21:43
Description:

"""
import random

from dianjing.exception import GameException

from core.mongo import MongoStaff, MongoTrainingShop, MongoCharacter
from core.training import TrainingShop, TrainingBroadcast, TrainingExp

from config import ConfigShop, ConfigClubLevel, ConfigErrorMessage


class TestTrainingShop(object):
    def setup(self):
        doc = MongoStaff.db(1).find_one({'_id': 1}, {'staffs': 1})
        staffs = doc['staffs']
        self.staff_id = int(random.choice(staffs.keys()))
        TrainingShop(1, 1)

    def teardown(self):
        MongoTrainingShop.db(1).drop()

    def test_cronjob(self):
        pass

    def test_staff_is_training(self):
        assert TrainingShop(1, 1).staff_is_training(self.staff_id) == False

        TrainingShop(1, 1).start(1, self.staff_id)
        assert TrainingShop(1, 1).staff_is_training(self.staff_id)

    def test_trig_open_by_club_level(self):
        conf = ConfigClubLevel.INSTANCES.keys()
        TrainingShop(1, 1).trig_open_by_club_level(conf.__len__())

        doc = MongoTrainingShop.db(1).find_one(
            {'_id': 1},
            {'shops': 1}
        )
        confs = ConfigShop.INSTANCES

        for k, v in confs.iteritems():
            if v.unlock_type == 2:
                assert str(k) in doc['shops'].keys()

    def test_trig_open_by_vip_level(self):
        confs = ConfigShop.INSTANCES
        level = 0
        for k, v in confs.iteritems():
            if v.unlock_type == 3:
                if level < v.unlock_value:
                    level = v.unlock_value

        TrainingShop(1, 1).trig_open_by_vip_level(level)
        doc = MongoTrainingShop.db(1).find_one(
            {'_id': 1},
            {'shops': 1}
        )
        for k, v in confs.iteritems():
            if v.unlock_type == 3:
                assert str(k) in doc['shops'].keys()


    def test_open(self):
        TrainingShop(1, 1)
        keys = ConfigShop.INSTANCES.keys()
        doc = MongoTrainingShop.db(1).find_one(
            {'_id': 1},
            {'shops': 1}
        )

        test_id = 0
        for key in keys:
            if str(key) not in doc['shops'].keys():
                test_id = key
                break

        TrainingShop(1, 1).open([test_id])
        new_doc = MongoTrainingShop.db(1).find_one(
            {'_id': 1},
            {'shops': 1}
        )
        assert str(test_id) in new_doc['shops'].keys()

    def test_start_shop_not_exist(self):
        staffs = MongoStaff.db(1).find_one({'_id': 1}, {'staffs': 1})
        staff_id = 0
        for i in range(1, 999):
            if str(i) not in staffs['staffs'].keys():
                staff_id = i
                break
        try:
            TrainingShop(1, 1).start(1, staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST")
        else:
            raise Exception('Error')

    def test_start_shop_not_open(self):
        conf = ConfigShop.INSTANCES.keys()

        test_id = 0
        doc = MongoTrainingShop.db(1).find_one({'_id': 1}, {'shops': 1})
        for key in conf:
            if key not in doc['shops']:
                test_id = key
                break
        try:
            TrainingShop(1, 1).start(test_id, self.staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_SHOP_NOT_OPEN")

    def test_start_in_broadcasting(self):
        TrainingBroadcast(1, 1).start(1, self.staff_id)
        try:
            TrainingShop(1, 1).start(1, self.staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_DOING_BROADCAST")
        else:
            raise Exception('Error')

    def test_start_in_exping(self):
        MongoCharacter.db(1).update_one({'_id': 1}, {'$set': {'club.gold': 1000000}})
        TrainingExp(1, 1).start(1, self.staff_id)
        try:
            TrainingShop(1, 1).start(1, self.staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_DOING_EXP")
        else:
            raise Exception('Error')

    def test_start_staff_in_training(self):
        TrainingShop(1, 1).open([2])
        TrainingShop(1, 1).start(2, self.staff_id)
        try:
            TrainingShop(1, 1).start(1, self.staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_SHOP_STAFF_IN_TRAINING")
        else:
            raise Exception('error')

    def test_send_notify(self):
        TrainingShop(1, 1).send_notify()
