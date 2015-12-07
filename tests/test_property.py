# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       test_property
Date Created:   2015-12-02 03:00
Description:

"""
import random
import arrow

from dianjing.exception import GameException

from core.mongo import MongoStaff, MongoCharacter, MongoTrainingProperty
from core.training import TrainingProperty
from core.bag import BagItem
from core.building import BuildingTrainingCenter
from core.training.property import PROPERTY_TRAINING_SLOTS_AMOUNT, PropertySlotStatus

from config import ConfigTrainingProperty, ConfigErrorMessage


def set_start_needed(training_id):
    conf = ConfigTrainingProperty.get(training_id)
    BagItem(1, 1).add(conf.need_items)

    if conf.cost_type == 1:
        needs = {'club.gold': conf.cost_value}
    else:
        needs = {'club.diamond': conf.cost_value}

    MongoCharacter.db(1).update_one(
        {'_id': 1},
        {'$set': needs},
        upsert=True
    )


def get_one_available_training(building_level):
    return random.choice(ConfigTrainingProperty.filter(need_building_level=building_level).keys())


class TestTrainingProperty(object):
    def setup(self):
        doc = MongoStaff.db(1).find_one({'_id': 1}, {'staffs': 1})
        staffs = doc['staffs']
        self.staff_id = int(random.choice(staffs.keys()))
        TrainingProperty(1, 1)

    def teardown(self):
        pass

    def test_staff_is_training(self):
        assert TrainingProperty(1, 1).staff_is_training(self.staff_id) == False

        training_id = get_one_available_training(1)
        set_start_needed(training_id)
        TrainingProperty(1, 1).start(self.staff_id, training_id)
        assert TrainingProperty(1, 1).staff_is_training(self.staff_id)

    def test_get_training_list(self):
        training_id = get_one_available_training(1)
        set_start_needed(training_id)
        TrainingProperty(1, 1).start(self.staff_id, training_id)
        assert TrainingProperty(1, 1).get_training_list(self.staff_id)

    def test_update_training_list(self):
        pass

    def test_start_staff_not_exist(self):
        doc = MongoStaff.db(1).find_one({'_id': 1}, {'staffs': 1})
        staffs = doc['staffs']

        staff_id = 0
        for i in range(1, 1000):
            if str(1) not in staffs.keys():
                staff_id = i
                break
        try:
            TrainingProperty(1, 1).start(staff_id, get_one_available_training(1))
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST")
        else:
            raise Exception('error')

    def test_start_property_not_exist(self):
        conf_keys = ConfigTrainingProperty.INSTANCES.keys()
        test_id = 0
        for i in range(1, 10000):
            if i not in conf_keys:
                test_id = i
                break
        try:
            TrainingProperty(1, 1).start(self.staff_id, test_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_NOT_EXIST")
        else:
            raise Exception('error')

    def test_start_center_level_not_enough(self):
        training_id = 0
        for k, v in ConfigTrainingProperty.INSTANCES.iteritems():
            if v.need_building_level > BuildingTrainingCenter(1, 1).current_level():
                training_id = k
                break

        try:
            TrainingProperty(1, 1).start(self.staff_id, training_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("BUILDING_TRAINING_CENTER_LEVEL_NOT_ENOUGH")
        else:
            raise Exception('error')

    def test_start_item_not_enough(self):
        try:
            TrainingProperty(1, 1).start(self.staff_id, get_one_available_training(1))
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("ITEM_NOT_ENOUGH")
        else:
            raise Exception('error')

    def test_start_list_full(self):
        training_id = get_one_available_training(1)

        for i in range(PROPERTY_TRAINING_SLOTS_AMOUNT):
            set_start_needed(training_id)
            TrainingProperty(1, 1).start(self.staff_id, training_id)

        try:
            set_start_needed(training_id)
            TrainingProperty(1, 1).start(self.staff_id, training_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_SLOT_FULL")
        else:
            raise Exception('error')

    def test_start(self):
        training_id = get_one_available_training(1)
        set_start_needed(training_id)
        TrainingProperty(1, 1).start(self.staff_id, training_id)

    def test_cancel_statue_not_waiting(self):
        training_id = get_one_available_training(1)

        for i in range(PROPERTY_TRAINING_SLOTS_AMOUNT):
            set_start_needed(training_id)
            TrainingProperty(1, 1).start(self.staff_id, training_id)

        try:
            TrainingProperty(1, 1).cancel(self.staff_id, 1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_CANCEL_CANNOT_EMPTY")
        else:
            raise Exception('error')

    def test_cancel(self):
        training_id = get_one_available_training(1)

        for i in range(PROPERTY_TRAINING_SLOTS_AMOUNT):
            set_start_needed(training_id)
            TrainingProperty(1, 1).start(self.staff_id, training_id)

        TrainingProperty(1, 1).cancel(self.staff_id, 2)

        assert TrainingProperty(1, 1).get_training_list(self.staff_id).slots[3].status == PropertySlotStatus.EMPTY

    def test_speedup_slot_empty(self):
        try:
            TrainingProperty(1, 1).speedup(self.staff_id, 1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('TRAINING_PROPERTY_SPEEDUP_CANNOT_EMPTY')
        else:
            raise Exception('error')

    def test_speedup_slot_waiting(self):
        training_id = get_one_available_training(1)

        for i in range(PROPERTY_TRAINING_SLOTS_AMOUNT):
            set_start_needed(training_id)
            TrainingProperty(1, 1).start(self.staff_id, training_id)

        try:
            TrainingProperty(1, 1).speedup(self.staff_id, 2)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('TRAINING_PROPERTY_SPEEDUP_CANNOT_WAITING')
        else:
            raise Exception('error')

    def test_speedup_slot_finish(self):
        training_id = get_one_available_training(1)

        for i in range(PROPERTY_TRAINING_SLOTS_AMOUNT):
            set_start_needed(training_id)
            TrainingProperty(1, 1).start(self.staff_id, training_id)

        try:
            TrainingProperty(1, 1).callback(self.staff_id)
            TrainingProperty(1, 1).speedup(self.staff_id, 1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_SPEEDUP_CANNOT_FINISH")

    def test_speedup(self):
        training_id = get_one_available_training(1)

        for i in range(PROPERTY_TRAINING_SLOTS_AMOUNT):
            set_start_needed(training_id)
            TrainingProperty(1, 1).start(self.staff_id, training_id)

        import formula
        need_diamond = formula.training_speedup_need_diamond(ConfigTrainingProperty.get(training_id).minutes * 60)

        MongoCharacter.db(1).update_one(
            {'_id': 1},
            {'$set': {'club.diamond': need_diamond}},
            upsert=True
        )
        TrainingProperty(1, 1).speedup(self.staff_id, 1)

    def test_get_reward_not_finish(self):
        training_id = get_one_available_training(1)

        for i in range(PROPERTY_TRAINING_SLOTS_AMOUNT):
            set_start_needed(training_id)
            TrainingProperty(1, 1).start(self.staff_id, training_id)

        try:
            TrainingProperty(1, 1).get_reward(self.staff_id, 1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_PROPERTY_REWARD_CANNOT")
        else:
            raise Exception('error')

    def test_get_reward(self):
        training_id = get_one_available_training(1)

        for i in range(PROPERTY_TRAINING_SLOTS_AMOUNT):
            set_start_needed(training_id)
            TrainingProperty(1, 1).start(self.staff_id, training_id)

        TrainingProperty(1, 1).callback(self.staff_id)
        TrainingProperty(1, 1).get_reward(self.staff_id, 1)

    def test_send_notify(self):
        TrainingProperty(1, 1).send_notify()

    def test_list(self):
        training_id = get_one_available_training(1)
        set_start_needed(training_id)
        TrainingProperty(1, 1).start(self.staff_id, training_id)
        # TrainingProperty(1, 1).callback(self.staff_id)

        set_start_needed(training_id)
        TrainingProperty(1, 1).start(self.staff_id, training_id)

        doc = MongoTrainingProperty.db(1).find_one({'_id': 1}, {'staffs': 1})
        print doc['staffs']

        conf = ConfigTrainingProperty.get(training_id)
        for slot in doc['staffs'][str(self.staff_id)]:
            if slot['end_at']:
                print slot['end_at'] - arrow.utcnow().timestamp, conf.minutes * 60


