# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       test_task
Date Created:   2015-08-06 09:33
Description:

"""
import random

from dianjing.exception import GameException

from core.mongo import MongoTask

from core.task import (
    get_target_current_value,
    TaskManager,
    TASK_STATUS_DOING,
    TASK_STATUS_FINISH,
    MAIN_TASK,
    DAILY_TASK,
)

from config import ConfigErrorMessage, ConfigTask, ConfigTaskTargetType


def get_not_exist_task_id():
        while 1:
            task_id = random.randint(1, 10000)
            if task_id not in ConfigTask.INSTANCES.keys():
                return task_id


def get_random_task_id(level=None):
    if not level:
        return random.choice(ConfigTask.INSTANCES.keys())
    return random.choice(ConfigTask.filter(level=level).keys())


class TestTask(object):
    def __init__(self):
        self.char_id = 1
        self.server_id = 1

    def set_finish_daily_task(self):
        task_ids = ConfigTask.filter(tp=DAILY_TASK, task_begin=True).keys()
        MongoTask.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'finish': task_ids}}
        )
        return task_ids

    def setup(self):
        MongoTask.db(self.server_id).update_one(
            {'_id': 1},
            {'$set': {
                'doing': {},
                'finish': [],
                'history': [],
            }},
            upsert=True,
        )

    def teardown(self):
        MongoTask.db(self.server_id).delete_one({'_id': self.char_id})

    def test_refresh(self):
        self.set_finish_daily_task()

        TaskManager(1, 1).refresh()
        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'history': 0})

        task_ids = ConfigTask.filter(tp=DAILY_TASK, task_begin=True)
        for task_id in task_ids:
            assert str(task_id) in doc['doing']
            assert task_id not in doc['finish']

    def test_add_task_not_exist(self):
        task_id = get_not_exist_task_id()
        try:
            TaskManager(1, 1).add_task(task_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('TASK_NOT_EXIST')
        else:
            raise Exception('error')

    def test_add_task_reduce(self):
        task_id = get_random_task_id()
        MongoTask.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$push': {'history': task_id}}
        )

        try:
            TaskManager(1, 1).add_task(task_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('TASK_CAN_NOT_REPRODUCE')
        else:
            raise Exception('error')

    def test_add_task(self):
        task_id = get_random_task_id()
        TaskManager(1, 1).add_task(task_id)

        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'doing': 1})
        assert str(task_id) in doc['doing']

    def test_get_reward_task_not_exist(self):
        task_id = get_not_exist_task_id()
        try:
            TaskManager(1, 1).get_reward(task_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('TASK_NOT_EXIST')
        else:
            raise Exception('error')

    def test_get_reward_task_not_done(self):
        task_id = get_random_task_id()
        try:
            TaskManager(1, 1).get_reward(task_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('TASK_NOT_DONE')
        else:
            raise Exception('error')

    def test_get_reward(self):
        task_id = random.choice(self.set_finish_daily_task())
        TaskManager(1, 1).get_reward(task_id)

        doc = MongoTask.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'finish': 1}
        )

        assert task_id not in doc['finish']

    def test_update(self):
        # judge will fail
        task_id = get_random_task_id()
        MongoTask.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'doing.{0}'.format(task_id): {}}}
        )

        task_config = ConfigTask.get(task_id)
        for key, value in task_config.targets.iteritems():
            TaskManager(1, 1).update(key[0], key[1], value)

        doc = MongoTask.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'finish': 1}
        )
        print doc['finish'], task_id
        assert task_id in doc['finish']

    def test_send_notify(self):
        TaskManager(1, 1).send_notify()

