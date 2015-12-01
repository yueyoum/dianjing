# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       test_broadcast
Date Created:   2015-12-01 04:41
Description:

"""
import random

from dianjing.exception import GameException
from config import ConfigErrorMessage, ConfigBuilding

from core.mongo import MongoStaff, MongoBuilding, MongoTrainingBroadcast, MongoCharacter
from core.training import TrainingBroadcast, TrainingExp, TrainingShop
from core.building import BuildingBusinessCenter

from core.training.broadcast import BROADCAST_TOTAL_SECONDS

from tests.test_training import set_enough_gold_and_diamond


class TestTrainingBroadcast(object):
    def setup(self):
        doc = MongoStaff.db(1).find_one({'_id': 1}, {'staffs': 1})
        staffs = doc['staffs']
        self.staff_id = int(random.choice(staffs.keys()))

    def teardown(self):
        pass

    def test_staff_is_training(self):
        assert TrainingBroadcast(1, 1).staff_is_training(self.staff_id) == False

        TrainingBroadcast(1, 1).start(1, self.staff_id)
        assert TrainingBroadcast(1, 1).staff_is_training(self.staff_id)

    def test_get_slot_not_exist(self):
        max_building_level = ConfigBuilding.get(BuildingBusinessCenter.BUILDING_ID).max_levels
        max_slots_amount = ConfigBuilding.get(BuildingBusinessCenter.BUILDING_ID).get_level(max_building_level).value2

        try:
            TrainingBroadcast(1, 1).get_slot(max_slots_amount + 1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_BROADCAST_SLOT_NOT_EXIST")
        else:
            raise Exception('Error')

    def test_get_slot_not_open(self):
        max_building_level = ConfigBuilding.get(BuildingBusinessCenter.BUILDING_ID).max_levels
        max_slots_amount = ConfigBuilding.get(BuildingBusinessCenter.BUILDING_ID).get_level(max_building_level).value2

        try:
            TrainingBroadcast(1, 1).get_slot(max_slots_amount)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_BROADCAST_SLOT_NOT_OPEN")
        else:
            raise Exception('Error')

    def test_get_slot(self):
        assert TrainingBroadcast(1, 1).get_slot(1)

    def test_start_staff_not_exist(self):
        staffs = MongoStaff.db(1).find_one({'_id': 1}, {'staffs': 1})
        staff_id = 0
        for i in range(1, 999):
            if str(i) not in staffs['staffs'].keys():
                staff_id = i
                break
        try:
            TrainingBroadcast(1, 1).start(1, staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST")
        else:
            raise Exception('Error')

    def test_start_slot_not_empty(self):
        TrainingBroadcast(1, 1).start(1, self.staff_id)
        try:
            TrainingBroadcast(1, 1).start(1, self.staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_BROADCAST_NOT_EMPTY")
        else:
            raise Exception('Error')

    def test_start_doing_exp(self):
        set_enough_gold_and_diamond(self.staff_id)
        TrainingExp(1, 1).start(1, self.staff_id)
        try:
            TrainingBroadcast(1, 1).start(1, self.staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_DOING_EXP")
        else:
            raise Exception('error')

    def test_start_doing_shop(self):
        TrainingShop(1, 1).start(1, self.staff_id)
        try:
            TrainingBroadcast(1, 1).start(1, self.staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_DOING_SHOP")
        else:
            raise Exception('error')

    def test_start_is_broadcasting(self):
        MongoBuilding.db(1).update_one(
            {'_id': 1},
            {'$set': {'buildings.{0}.level'.format(BuildingBusinessCenter.BUILDING_ID): 2}},
            upsert=True
        )
        TrainingBroadcast(1, 1).open_slots_by_building_level_up()

        TrainingBroadcast(1, 1).start(1, self.staff_id)
        try:
            TrainingBroadcast(1, 1).start(2, self.staff_id)
        except GameException as e:
            print e.error_id
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_BROADCAST_STAFF_IN_TRAINING")
        else:
            raise Exception('error')

    def test_start(self):
        MongoTrainingBroadcast.db(1).delete_one({'_id': 1})
        TrainingBroadcast(1, 1).start(1, self.staff_id)

        data = MongoTrainingBroadcast.db(1).find_one({'_id': 1}, {'slots.{0}'.format(1): 1})
        assert data['slots']['1']['staff_id'] == self.staff_id

    def test_cancel_not_broadcast(self):
        try:
            TrainingBroadcast(1, 1).cancel(1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_BROADCAST_NOT_TRAINING")
        else:
            raise Exception('Error')

    def test_cancel(self):
        TrainingBroadcast(1, 1).start(1, self.staff_id)
        TrainingBroadcast(1, 1).cancel(1)

        data = MongoTrainingBroadcast.db(1).find_one({'_id': 1}, {'slots': 1})
        if data['slots'].get(str(1), None):
            raise Exception('error')

    def test_speedup_not_enough_diamond(self):
        try:
            TrainingBroadcast(1, 1).start(1, self.staff_id)
            TrainingBroadcast(1, 1).speedup(1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("DIAMOND_NOT_ENOUGH")
        else:
            raise Exception('Error')

    def test_speedup(self):
        TrainingBroadcast(1, 1).start(1, self.staff_id)
        import formula
        diamonds = formula.training_speedup_need_diamond(BROADCAST_TOTAL_SECONDS)
        MongoCharacter.db(1).update_one(
            {'_id': 1},
            {'$set': {'club.diamond': diamonds}},
            upsert=True
        )
        TrainingBroadcast(1, 1).speedup(1)

        data = MongoTrainingBroadcast.db(1).find_one({'_id': 1}, {'slots.{0}'.format(1): 1})
        assert data['slots'][str(1)]['gold'] > -1

    def test_callback(self):
        TrainingBroadcast(1, 1).start(1, int(self.staff_id))
        TrainingBroadcast(1, 1).callback(1)
        doc = MongoTrainingBroadcast.db(1).find_one({"_id": 1}, {"slots": 1})
        assert doc['slots']['1']['gold'] > -1

    def test_get_reward_not_finish(self):
        TrainingBroadcast(1, 1).start(1, int(self.staff_id))
        try:
            TrainingBroadcast(1, 1).get_reward(1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_BROADCAST_NOT_FINISH")
        else:
            raise Exception('error')

    def test_get_reward(self):
        TrainingBroadcast(1, 1).start(1, int(self.staff_id))
        TrainingBroadcast(1, 1).callback(1)
        TrainingBroadcast(1, 1).get_reward(1)

        data = MongoCharacter.db(1).find_one({'_id': 1}, {'club.gold'.format(self.staff_id): 1})
        assert data['club']['gold'] > 0

    def test_send_notify(self):
        TrainingBroadcast(1, 1).send_notify()

