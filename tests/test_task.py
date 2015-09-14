# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       test_task
Date Created:   2015-08-06 09:33
Description:

"""
import random

from dianjing.exception import GameException

from core.db import MongoDB
from core.common import CommonTask
from core.building import BuildingTaskCenter

from core.task import (
    TaskManager,
    TaskRefresh,
    TASK_STATUS_DOING,
    TASK_STATUS_UNRECEIVED,
    TASK_STATUS_FINISH,
    TASK_STATUS_END,
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
    BUILDING_LEVEL = 1

    @classmethod
    def setup_class(cls):
        # 设置 任务中心 等级
        MongoDB.get(1).building.update_one(
            {'_id': 1},
            {'$set': {'buildings.{0}'.format(BuildingTaskCenter.BUILDING_ID): cls.BUILDING_LEVEL}},
             upsert=True
        )

    @classmethod
    def teardown_class(cls):
        MongoDB.get(1).building.delete_one({'_id': 1})

    def setup(self):
        self.reset()

    def teardown(self):
        self.reset()

    def reset(self):
        MongoDB.get(1).task.delete_one({'_id': 1})

    def set_task_status(self, task_id, status):
        MongoDB.get(1).task.update_one(
            {'_id': 1},
            {'$set': {
                'tasks.{0}'.format(task_id): {
                    'num': 0,
                    'status': status
                }
            }},
            upsert=True
        )

    def test_common_refresh(self):
        TaskRefresh(1).refresh()
        value = CommonTask.get(1)
        assert len(value) > 0


    def test_refresh(self):
        TaskManager(1, 1).refresh()
        data = MongoDB.get(1).task.find_one({'_id': 1})
        assert len(data['tasks']) > 0


    def test_receive_not_exist(self):
        random_id = get_none_exist_task_id()
        try:
            TaskManager(1, 1).receive(random_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TASK_NOT_EXIST")
        else:
            raise Exception("can not be here")


    def test_receive_level_not_enough(self):
        task_id = get_random_task_id(level=self.BUILDING_LEVEL+1)

        try:
            TaskManager(1, 1).receive(task_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("BUILDING_TASK_CENTER_LEVEL_NOT_ENOUGH")
        else:
            raise Exception("can not be here")


    # def test_receive_not_find(self):
    #     try:
    #         TaskManager(1, 1).receive(9999)
    #     except GameException as e:
    #         assert e.error_id == ConfigErrorMessage.get_error_id("TASK_NOT_FIND")
    #     else:
    #         raise Exception("can not be here")


    def test_receive_already_doing(self):
        task_id = get_random_task_id(level=self.BUILDING_LEVEL)

        self.set_task_status(task_id, TASK_STATUS_DOING)

        try:
            TaskManager(1, 1).receive(task_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id('TASK_ALREADY_DOING')
        else:
            raise Exception('test_receive_already_doing error')


    def test_receive(self):
        task_ids = TaskManager(1, 1).refresh()

        tid = random.choice(task_ids)
        TaskManager(1, 1).receive(tid)

        doc = MongoDB.get(1).task.find_one({'_id': 1})
        assert doc['tasks'][str(tid)]['status'] == TASK_STATUS_DOING


    def test_get_reward_task_not_exist(self):
        task_id = get_none_exist_task_id()

        try:
            TaskManager(1, 1).get_reward(task_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TASK_NOT_EXIST")
        else:
            raise Exception('test get reward task not exist error')


    def test_get_reward_task_not_done(self):
        task_id = get_random_task_id(level=self.BUILDING_LEVEL)

        self.set_task_status(task_id, TASK_STATUS_DOING)
        try:
            TaskManager(1, 1).get_reward(task_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TASK_NOT_DONE")
        else:
            raise Exception('test_get_reward_task_not_done error')


    def test_get_reward_have_got(self):
        task_id= get_random_task_id(level=self.BUILDING_LEVEL)

        self.set_task_status(task_id, TASK_STATUS_END)
        try:
            TaskManager(1, 1).get_reward(task_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TASK_ALREADY_GET_REWARD")
        else:
            raise Exception('test_get_reward_have_got error')


    def test_get_reward(self):
        task_id = get_random_task_id(level=self.BUILDING_LEVEL)

        self.set_task_status(task_id, TASK_STATUS_FINISH)
        TaskManager(1, 1).get_reward(task_id)


    def test_send_notify(self):
        TaskManager(1, 1).send_notify()


    def test_update(self):
        task_id = get_random_task_id(level=self.BUILDING_LEVEL)
        self.set_task_status(task_id, TASK_STATUS_DOING)

        config = ConfigTask.get(task_id)
        TaskManager(1, 1).trig(config.tp, config.num)

        doc = MongoDB.get(1).task.find_one({'_id': 1})

        assert doc['tasks'][str(task_id)]['num'] == ConfigTask.get(task_id).num
        assert doc['tasks'][str(task_id)]['status'] == TASK_STATUS_FINISH


    def test_update_no_change(self):
        task_id = get_random_task_id(level=self.BUILDING_LEVEL)
        self.set_task_status(task_id, TASK_STATUS_FINISH)

        config = ConfigTask.get(task_id)
        TaskManager(1, 1).trig(config.tp, config.num)

        doc = MongoDB.get(1).task.find_one({'_id': 1})

        assert doc['tasks'][str(task_id)]['num'] == 0
        assert doc['tasks'][str(task_id)]['status'] == TASK_STATUS_FINISH
