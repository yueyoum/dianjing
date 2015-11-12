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
    TaskManager,
    TASK_STATUS_DOING,
    TASK_STATUS_FINISH,
    DAILY_TASK,
)

from config import ConfigErrorMessage, ConfigTask


def get_none_exist_task_id():
    while 1:
        task_id = random.randint(1, 10000)
        if task_id not in ConfigTask.INSTANCES.keys():
            return task_id


def get_random_task_id(level=None):
    if not level:
        return random.choice(ConfigTask.INSTANCES.keys())
    return random.choice(ConfigTask.filter(level=level).keys())


class TestTask(object):
    def setup(self):
        MongoTask.db(1).update_one(
            {'_id': 1},
            {'$set': {
                'doing': {},
                'finish': [],
                'history': [],
            }},
            upsert=True,
        )

    def teardown(self):
        MongoTask.db(1).delete_one({'_id': 1})

    def test_refresh(self):
        TaskManager(1, 1).refresh()
        data = MongoTask.db(1).find_one({'_id': 1}, {'doing': 1})
        doing_ids = data['doing'].keys()

        task_ids = ConfigTask.filter(tp=DAILY_TASK, task_begin=True)

        for task_id in task_ids:
            assert str(task_id) in doing_ids

    def test_add_task_not_exist(self):
        task_ids = ConfigTask.INSTANCES.keys()
        test_id = 0
        for i in range(10000, 2000):
            if i not in task_ids:
                test_id = i

        try:
            TaskManager(1, 1).add_task(test_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('TASK_NOT_EXIST')
        else:
            raise Exception('error')

    def test_add_task(self):
        task_id = random.choice(ConfigTask.INSTANCES.keys())
        TaskManager(1, 1).add_task(task_id)

        doc = MongoTask.db(1).find_one({'_id': 1}, {'doing': 1})
        assert doc['doing'][str(task_id)]

    def test_update(self):
        task_id = random.choice(ConfigTask.INSTANCES.keys())
        TaskManager(1, 1).add_task(task_id)
        task = ConfigTask.get(task_id)

        target_id = random.choice(task.targets.keys())
        num = task.targets[target_id]
        TaskManager(1, 1).update(target_id, num)

        data = MongoTask.db(1).find_one({'_id': 1}, {'finish': 1})
        assert task_id in data['finish']



