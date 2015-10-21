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

from core.mongo import MongoCharacter, MongoTrainingExp, MongoStaff, MongoBuilding
from core.training import TrainingExp
from core.club import Club
from core.building import BuildingTrainingCenter, BUILDING_TRAINING_CENTER

from config import ConfigErrorMessage, ConfigStaff, ConfigBuilding

NOT_EXIST = 1
NOT_OPEN = 2
EMPTY = 3
TRAINING = 4
FINISH = 5


class TestTrainingExp(object):
    def reset(self):
        MongoCharacter.db(1).update_one(
            {'_id': 1},
            {'$set': {'club.level': 3}}
        )
        self.staff_id = random.choice(ConfigStaff.INSTANCES.keys())
        TrainingExp(1, 1)

        MongoStaff.db(1).update_one(
            {'_id': 1},
            {'$set': {'staffs.{0}'.format(self.staff_id): {'exp': 0, 'level': 1, 'status': 3,
                                                           'skills': {}, 'trainings': [],
                                                           'winning_rate': {}}}}
        )

    def setup(self):
        self.reset()

    def teardown(self):
        self.reset()
        MongoTrainingExp.db(1).drop()

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

    def test_start_slot_not_exist(self):
        max_building_level = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).max_levels
        max_slots_amount = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).get_level(max_building_level).value2
        try:
            TrainingExp(1, 1).start(max_slots_amount + 1, self.staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_NOT_EXIST")
        else:
            raise Exception('Error')

    def test_start_slot_not_open(self):
        current_slots_amount = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).get_level(1).value2
        try:
            TrainingExp(1, 1).start(current_slots_amount + 1, self.staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_NOT_OPEN")
        else:
            raise Exception('Error')

    def test_start_slot_in_use(self):
        MongoTrainingExp.db(1).update_one(
            {'_id': 1},
            {'$set': {'slots.{0}'.format(1): {'staff_id': self.staff_id,
                                              'start_at': arrow.utcnow().timestamp,
                                              'time_point': 0,
                                              'exp': 0,
                                              'speedup': False}}},
        )

        try:
            TrainingExp(1, 1).start(1, self.staff_id)
        except GameException as e:
            print e.error_id
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_EXP_SLOT_IN_USE")
        else:
            raise Exception('Error')

    def test_start_staff_in_training(self):
        MongoTrainingExp.db(1).update_one(
            {'_id': 1},
            {'$set': {'slots.{0}'.format(1): {'staff_id': self.staff_id,
                                              'start_at': arrow.utcnow().timestamp,
                                              'time_point': 0,
                                              'exp': 0,
                                              'speedup': False}}},
        )

        MongoBuilding.db(1).update_one(
            {'_id': 1},
            {'$set': {'buildings.{0}.current_level'.format(BUILDING_TRAINING_CENTER): 3}}
        )
        try:
            TrainingExp(1, 1).start(2, self.staff_id)
        except GameException as e:
            print e.error_id
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_EXP_STAFF_IN_TRAINING")
        else:
            raise Exception('Error')

    def test_start(self):
        Club(1, 1).update(gold=8000)
        MongoTrainingExp.db(1).delete_one({'_id': 1})
        TrainingExp(1, 1).start(1, self.staff_id)
        data = MongoTrainingExp.db(1).find_one({'_id': 1}, {'slots.{0}'.format(1): 1})
        assert data['slots']['1']['staff_id'] == self.staff_id

    def test_cancel_cannot_operate(self):
        MongoTrainingExp.db(1).update_one(
            {'_id': 1},
            {'$set': {'slots.{0}'.format(1): {'staff_id': self.staff_id,
                                              'start_at': arrow.utcnow().timestamp,
                                              'time_point': 0,
                                              'exp': 0,
                                              'speedup': True}}},
        )
        doc = MongoTrainingExp.db(1).find_one(
            {'_id': 1},
            {'slots.{0}'.format(1): 1}
        )
        print doc

        try:
            TrainingExp(1, 1).cancel(1)
        except GameException as e:
            print e.error_id
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_EXP_FINISH_CANNOT_OPERATE")

    def test_cancel(self):
        MongoTrainingExp.db(1).update_one(
            {'_id': 1},
            {'$set': {'slots.{0}'.format(1): {'staff_id': self.staff_id,
                                              'start_at': arrow.utcnow().timestamp,
                                              'time_point': 0,
                                              'exp': 0,
                                              'speedup': False}}},
        )

        TrainingExp(1, 1).cancel(1)

        data = MongoTrainingExp.db(1).find_one({'_id': 1}, {'slots': 1})

        if data['slots'].get(str(1), None):
            raise Exception('error')

    def test_speedup(self):
        Club(1, 1).update(diamond=8000, gold=8000)
        TrainingExp(1, 1).start(1, self.staff_id)
        TrainingExp(1, 1).speedup(1)

        data = MongoTrainingExp.db(1).find_one({'_id': 1}, {'slots.{0}'.format(1): 1})
        assert data['slots'][str(1)]['speedup'] == True

    def test_get_reward_not_finish(self):
        Club(1, 1).update(gold=8000)
        TrainingExp(1, 1).start(1, self.staff_id)
        try:
            TrainingExp(1, 1).get_reward(1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_EXP_NOT_FINISH")
        else:
            raise Exception('error')

    def test_get_reward(self):
        Club(1, 1).update(gold=8000, diamond=8000)
        TrainingExp(1, 1).start(1, self.staff_id)
        TrainingExp(1, 1).speedup(1)
        TrainingExp(1, 1).get_reward(1)
        data = MongoStaff.db(1).find_one({'_id': 1}, {'staffs.{0}'.format(self.staff_id): 1})
        assert data['staffs'][str(self.staff_id)]['exp'] > 0

    def test_clean(self):
        Club(1, 1).update(gold=8000, diamond=8000)
        TrainingExp(1, 1).start(1, self.staff_id)
        TrainingExp(1, 1).clean(1)
        data = MongoTrainingExp.db(1).find_one({'_id': 1}, {'slots.1': 1})
        assert data['slots'][str(1)] == {}

    def test_send_notify(self):
        TrainingExp(1, 1).send_notify([1])
