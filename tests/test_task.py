# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       test_task
Date Created:   2015-08-06 09:33
Description:

"""
import random

from dianjing.exception import GameException

# from .data4test import *

# task test data
test_centre_lv = 1
test_task_id = 1

# common test data
test_server_id = 1
test_char_id = 1

league_centre_id = 5
task_centre_id = 4
staff_centre_id = 3
entertainment_centre_id = 2
training_centre_id = 1

from core.db import MongoDB
from config import ConfigErrorMessage, ConfigTask, ConfigBuilding

from core.task import TaskManager, TaskRefresh


def get_out_random_id():
    while 1:
        task_id = random.randint(1, 10000)
        if task_id not in ConfigTask.INSTANCES.keys():
            return task_id

def get_high_level_task(levels):
    max_level = ConfigBuilding.get(task_centre_id).max_levels
    if max_level <= levels:
        Exception("error level")
    else:
        task_ids = ConfigTask.filter(level=levels+1)
        return random.sample(task_ids, 1)



class TestTask(object):

    def reset(self):
        mongo = MongoDB.get(test_server_id)
        mongo.task.update_one(
            {'_id': 1},
            {'$set': {'tasks.{0}'.format(test_task_id): {'num': 0, 'status': 0}}},
            upsert=True
        )

    def update_receive(self):
        mongo = MongoDB.get(test_server_id)
        mongo.task.update_one(
            {'_id': 1},
            {'$set': {'tasks.{0}'.format(test_task_id): {'num': 0, 'status': 1}}}
        )

    def update_got_reward(self):
        mongo = MongoDB.get(test_server_id)
        mongo.task.update_one(
            {'_id': 1},
            {'$set': {'tasks.{0}'.format(test_task_id): {'num': 0, 'status': 3}}}
        )

    def setUp(self):
        # print 'setUp'
        self.reset()

    def tearDown(self):
        # print 'teardown'
        self.reset()

    def test_common_refresh(self):
        TaskRefresh(test_server_id).refresh()
        data = MongoDB.get(test_server_id).common.find_one({'_id': TaskRefresh.TASK_COMMON_MONGO_ID})
        if not data['levels']:
            raise Exception("common refresh error")

    def test_refresh(self):
        MongoDB.get(test_server_id).building.update_one(
            {'_id': test_char_id},
            {'$set': {'buildings.{0}'.format(task_centre_id): 1}},
             upsert=True
        )
        TaskManager(test_server_id, test_char_id).refresh()
        data = MongoDB.get(test_server_id).task.find_one({'_id': test_char_id})
        if not data['tasks'][str(test_task_id)]:
            raise Exception('refresh error')

    def test_receive_not_exist(self):
        random_id = get_out_random_id
        try:
            TaskManager(test_server_id, test_char_id).receive(random_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TASK_NOT_EXIST")
        else:
            raise Exception("can not be here")

    def test_receive_level_not_enough(self):
        task_id = get_high_level_task(test_centre_lv)
        try:
            TaskManager(test_server_id, test_char_id).receive(task_id[0])
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("CLUB_LEVEL_NOT_ENOUGH")
        else:
            raise Exception("can not be here")

    def test_receive_already_doing(self):
        self.update_receive()
        try:
            TaskManager(test_server_id, test_char_id).receive(test_task_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('TASK_ALREADY_DOING')
        else:
            raise Exception('test_receive_already_doing error')

    def test_get_reward_task_not_exist(self):
        task_id = get_out_random_id()
        try:
            TaskManager(test_server_id,test_char_id).get_reward(task_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TASK_NOT_EXIST")
        else:
            raise Exception('test get reward task not exist error')

    def test_get_reward_task_not_done(self):
        self.update_receive()
        try:
            TaskManager(test_server_id, test_char_id).get_reward(test_task_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TASK_NOT_DONE")
        else:
            raise Exception('test_get_reward_task_not_done error')

    def test_get_reward_have_got(self):
        self.update_got_reward()
        try:
            TaskManager(test_server_id, test_char_id).get_reward(test_task_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TASK_ALREADY_GET_REWARD")
        else:
            Exception('test_get_reward_have_got error')

    def test_send_notify(self):
        pass

    def test_update(self):
        self.update_receive()

        doc = {
            'task_id': test_task_id,
            'num': 1,
        }
        TaskManager(test_server_id, test_char_id).update(**doc)
        task_data = MongoDB.get(test_server_id).task.find_one({'_id': test_char_id},
                                                              {'tasks.{0}'.format(test_char_id): 1})
        task = task_data['tasks'][str(test_char_id)]
        assert task['status'] == 2

    def test_get_task_ids(self):
        pass



