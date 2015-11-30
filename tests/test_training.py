# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_training
Date Created:   2015-08-05 17:42
Description:

"""
import random
import arrow


from dianjing.exception import GameException

from core.mongo import MongoTrainingExp, MongoStaff, MongoBuilding, MongoCharacter
from core.training import TrainingExp, TrainingBroadcast, TrainingShop

from core.building import BuildingTrainingCenter
from core.staff import staff_training_exp_need_gold, staff_level_up_need_exp, StaffManger

from config import ConfigErrorMessage, ConfigStaff, ConfigBuilding
from core.package import Property


def set_slot_test_data(staff_id, slot_id):
    MongoTrainingExp.db(1).update_one(
        {'_id': 1},
        {'$set': {'slots.{0}'.format(slot_id): {'staff_id': staff_id,
                                                'start_at': arrow.utcnow().timestamp,
                                                'exp': -1,
                                                'key': ''}}},
    )


def get_valid_slot():
    return ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).get_level(1).value2 - 1


def set_enough_gold_and_diamond(staff_id):
    MongoCharacter.db(1).update_one(
        {'_id': 1},
        {'$set': {'club.gold': staff_training_exp_need_gold(staff_id, 1),
                  'club.diamond': 8000}}
    )


class TestTrainingExp(object):
    def setup(self):
        doc = MongoStaff.db(1).find_one({'_id': 1}, {'staffs': 1})
        staffs = doc['staffs']
        self.staff_id = random.choice(staffs.keys())
        set_enough_gold_and_diamond(self.staff_id)

    def teardown(self):
        MongoTrainingExp.db(1).drop()

    def test_staff_is_training(self):
        assert TrainingExp(1, 1).staff_is_training(self.staff_id) == False

        set_slot_test_data(self.staff_id, 1)
        assert TrainingExp(1, 1).staff_is_training(self.staff_id)

    def test_open_slots_by_building_level_up(self):
        pass

    def test_get_slot_not_exist(self):
        max_building_level = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).max_levels
        max_slots_amount = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).get_level(max_building_level).value2

        try:
            TrainingExp(1, 1).get_slot(max_slots_amount + 1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_NOT_EXIST")
        else:
            raise Exception('Error')

    def test_get_slot_not_open(self):
        current_slots_amount = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).get_level(1).value2
        try:
            TrainingExp(1, 1).get_slot(current_slots_amount + 1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_NOT_OPEN")
        else:
            raise Exception('Error')

    def test_get_slot(self):
        assert TrainingExp(1, 1).get_slot(1)

    def test_start_staff_not_exist(self):
        staffs = MongoStaff.db(1).find_one({'_id': 1}, {'staffs': 1})
        staff_id = 0
        for i in range(1, 999):
            if str(i) not in staffs['staffs'].keys():
                staff_id = i
                break
        try:
            TrainingExp(1, 1).start(1, staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST")
        else:
            raise Exception('Error')

    def test_start_slot_in_use(self):
        TrainingExp(1, 1).start(1, int(self.staff_id))
        try:
            TrainingExp(1, 1).start(1, int(self.staff_id))
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_IN_USE")
        else:
            raise Exception('Error')

    def test_start_staff_doing_broadcast(self):
        TrainingBroadcast(1, 1).start(1, int(self.staff_id))
        try:
            TrainingExp(1, 1).start(1, int(self.staff_id))
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_DOING_BROADCAST")
        else:
            raise Exception('error')

    def test_start_staff_doing_shop(self):
        TrainingShop(1, 1).start(1, int(self.staff_id))
        try:
            TrainingExp(1, 1).start(1, int(self.staff_id))
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_DOING_SHOP")
        else:
            raise Exception('error')

    def test_start_staff_in_training(self):
        MongoBuilding.db(1).update_one(
            {'_id': 1},
            {'$set': {'buildings.{0}.current_level'.format(BuildingTrainingCenter.BUILDING_ID): 3}}
        )
        try:
            TrainingExp(1, 1).start(1, int(self.staff_id))
            TrainingExp(1, 1).start(2, int(self.staff_id))
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_EXP_STAFF_IN_TRAINING")
        else:
            raise Exception('Error')

    def test_start_gold_not_enough(self):
        MongoCharacter.db(1).update_one(
            {'_id': 1},
            {'$set': {'club.gold': 0}}
        )
        MongoTrainingExp.db(1).delete_one({'_id': 1})
        try:
            TrainingExp(1, 1).start(1, int(self.staff_id))
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("GOLD_NOT_ENOUGH")
        else:
            raise Exception('error')

    def test_start(self):
        MongoTrainingExp.db(1).delete_one({'_id': 1})
        TrainingExp(1, 1).start(1, int(self.staff_id))

        data = MongoTrainingExp.db(1).find_one({'_id': 1}, {'slots.{0}'.format(1): 1})
        assert data['slots']['1']['staff_id'] == int(self.staff_id)
        gold = MongoCharacter.db(1).find_one({'_id': 1}, {'club.gold': 1})
        assert gold['club']['gold'] == 0

    def test_cancel_slot_empty(self):
        try:
            TrainingExp(1, 1).cancel(1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_EMPTY")
        else:
            raise Exception('Error')

    def test_cancel_cannot_operate(self):
        try:
            TrainingExp(1, 1).start(1, int(self.staff_id))
            TrainingExp(1, 1).speedup(1)
            TrainingExp(1, 1).cancel(1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_EXP_FINISH_CANNOT_OPERATE")
        else:
            raise Exception('error')

    def test_cancel(self):
        TrainingExp(1, 1).start(1, int(self.staff_id))
        TrainingExp(1, 1).cancel(1)

        data = MongoTrainingExp.db(1).find_one({'_id': 1}, {'slots': 1})
        if data['slots'].get(str(1), None):
            raise Exception('error')

    def test_speedup(self):
        TrainingExp(1, 1).start(1, int(self.staff_id))
        TrainingExp(1, 1).speedup(1)

        data = MongoTrainingExp.db(1).find_one({'_id': 1}, {'slots.{0}'.format(1): 1})
        assert data['slots'][str(1)]['exp'] >= -1
        gold = MongoCharacter.db(1).find_one({'_id': 1}, {'club.gold': 1})
        assert gold['club']['gold'] == 0

    def test_callback(self):
        TrainingExp(1, 1).start(1, int(self.staff_id))
        TrainingExp(1, 1).callback(1)
        doc = MongoTrainingExp.db(1).find_one({"_id": 1}, {"slots": 1})
        assert doc['slots']['1']['exp'] > -1

    def test_get_reward_not_finish(self):
        TrainingExp(1, 1).start(1, int(self.staff_id))
        try:
            TrainingExp(1, 1).get_reward(1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_EXP_NOT_FINISH")
        else:
            raise Exception('error')

    def test_get_reward(self):
        TrainingExp(1, 1).start(1, int(self.staff_id))
        TrainingExp(1, 1).speedup(1)
        TrainingExp(1, 1).get_reward(1)

        data = MongoStaff.db(1).find_one({'_id': 1}, {'staffs.{0}'.format(self.staff_id): 1})
        assert data['staffs'][str(self.staff_id)]['exp'] > 0

    def test_clean(self):
        TrainingExp(1, 1).start(1, int(self.staff_id))
        TrainingExp(1, 1).clean(1)
        data = MongoTrainingExp.db(1).find_one({'_id': 1}, {'slots.1': 1})
        assert data['slots'][str(1)] == {}

    def test_send_notify(self):
        TrainingExp(1, 1).send_notify([1])


