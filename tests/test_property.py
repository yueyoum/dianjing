# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       test_property
Date Created:   2015-12-02 03:00
Description:

"""
import random

from core.mongo import MongoStaff, MongoCharacter
from core.training import TrainingProperty


def set_start_needed(staff_id):
    pass


class TestTrainingProperty(object):
    def setup(self):
        doc = MongoStaff.db(1).find_one({'_id': 1}, {'staffs': 1})
        staffs = doc['staffs']
        self.staff_id = int(random.choice(staffs.keys()))
        TrainingProperty(1, 1)

    def teardown(self):
        pass

    def test_staff_is_training(self):
        pass

    def test_get_training_list(self):
        pass

    def test_update_training_list(self):
        pass

    def test_start_staff_not_exist(self):
        pass

    def test_start_property_not_exist(self):
        pass

    def test_start_center_level_not_enough(self):
        pass

    def test_start_item_not_enough(self):
        pass

    def test_start_list_full(self):
        pass

    def test_start(self):
        pass

    def test_cancel_statue_not_waiting(self):
        pass

    def test_cancel(self):
        pass
