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
from core.task import TaskManager, MAIN_TASK, DAILY_TASK
from config import ConfigErrorMessage, ConfigTask


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

    def set_task_finish(self, task_id):
        MongoTask.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$push': {'finish': task_id}},
            upsert=True
        )

    def set_mongodb_task_finish(self):
        old_doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'doing': 1})
        for task_id in old_doc['doing']:
            conf_task = ConfigTask.get(int(task_id))
            for k, v in conf_task.targets.iteritems():
                TaskManager(self.server_id, self.char_id).update(k[0], k[1], v)
        return [int(task_id) for task_id in old_doc['doing'].keys()]

    def get_mongodb_task_doing_ids(self):
        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'doing': 1})
        return [int(task_id) for task_id in doc['doing'].keys()]

    def setup(self):
        TaskManager(self.server_id, self.char_id)

    def teardown(self):
        MongoTask.db(self.server_id).delete_one({'_id': self.char_id})

    def test_refresh(self):
        daily_ids = []
        main_ids = []

        task_ids = self.set_mongodb_task_finish()
        for task_id in task_ids:
            conf_task = ConfigTask.get(int(task_id))
            if conf_task.tp == DAILY_TASK:
                daily_ids.append(task_id)

            if conf_task == MAIN_TASK:
                main_ids.append(task_id)

        TaskManager(self.server_id, self.char_id).refresh()
        new_doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'history': 0})

        for task_id in daily_ids:
            assert str(task_id) in new_doc['doing']
            assert task_id not in new_doc['finish']

        for task_id in main_ids:
            assert str(task_id) not in new_doc['doing']
            assert task_id in task_ids

    def test_add_task_not_exist(self):
        task_id = get_not_exist_task_id()
        try:
            TaskManager(self.server_id, self.char_id).add_task(task_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('TASK_NOT_EXIST')
        else:
            raise Exception('error')

    def test_add_task_just_doing(self):
        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'doing': 1})
        for task_id in doc['doing']:
            try:
                TaskManager(self.server_id, self.char_id).add_task(int(task_id))
            except GameException as e:
                assert e.error_id == ConfigErrorMessage.get_error_id('TASK_ALREADY_DOING')
            else:
                raise Exception('error')

    def test_add_task_reduce(self):
        task_id = get_random_task_id()
        MongoTask.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$push': {'history': task_id}}
        )

        try:
            TaskManager(self.server_id, self.char_id).add_task(task_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('TASK_CAN_NOT_REPRODUCE')
        else:
            raise Exception('error')

    def test_add_task(self):
        task_id = get_random_task_id()
        TaskManager(self.server_id, self.char_id).add_task(task_id)

        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'doing': 1})
        assert str(task_id) in doc['doing']

    def test_get_reward_task_not_exist(self):
        task_id = get_not_exist_task_id()
        try:
            TaskManager(self.server_id, self.char_id).get_reward(task_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('TASK_NOT_EXIST')
        else:
            raise Exception('error')

    def test_get_reward_task_not_done(self):
        task_id = get_random_task_id()
        try:
            TaskManager(self.server_id, self.char_id).get_reward(task_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('TASK_NOT_DONE')
        else:
            raise Exception('error')

    def test_get_reward(self):
        task_ids = self.set_mongodb_task_finish()
        for task_id in task_ids:
            TaskManager(self.server_id, self.char_id).get_reward(task_id)

        new_doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'history': 0})
        for task_id in new_doc['finish']:
            assert task_id not in new_doc['doing']
            assert task_id not in new_doc['finish']

    def test_trigger(self):
        task_ids = self.set_mongodb_task_finish()

        test_ids = []
        for task_id in task_ids:
            TaskManager(self.server_id, self.char_id).get_reward(task_id)
            conf = ConfigTask.get(task_id)
            if conf.tp == MAIN_TASK:
                test_ids.append(task_id)
                TaskManager(self.server_id, self.char_id).trigger(conf.trigger, conf.trigger_value)

        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'history': 0})
        for task_id in test_ids:
            assert task_id not in doc['doing']
            assert task_id not in doc['finish']

    def test_update(self):
        task_ids = self.get_mongodb_task_doing_ids()

        for task_id in task_ids:
            conf_task = ConfigTask.get(int(task_id))
            for k, v in conf_task.targets.iteritems():
                TaskManager(self.server_id, self.char_id).update(k[0], k[1], v)

        doc = MongoTask.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'finish': 1}
        )

        for task_id in task_ids:
            assert task_id in doc['finish']

    def test_send_notify(self):
        TaskManager(self.server_id, self.char_id).send_notify()
