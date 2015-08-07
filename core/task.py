# -*- coding:utf-8 -*-

__author__ = 'hikaly'

import random

from dianjing.exception import GameException

from core.db import get_mongo_db
from core.mongo import Document, MONGO_COMMON_KEY_TASK
from core.resource import Resource
from core.building import BuildingManager
from core.common import Common

from config import ConfigErrorMessage
from config.task import ConfigTask
from config.building import ConfigBuilding

from utils.message import MessagePipe

from protomsg.task_pb2 import TaskNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE

TASK_STATUS_UNRECEIVED = 0
TASK_STATUS_DOING = 1
TASK_STATUS_FINISH = 2
TASK_STATUS_END = 3


TASK_CENTRE_ID = 4
# 每个等级要刷新的任务数量
TASK_REFRESH_AMOUNT_PER_LEVEL = 10


class TaskRefresh(object):
    def __init__(self, server_id):
        self.server_id = server_id
        self.mongo = get_mongo_db(server_id)


    @classmethod
    def cron_job(cls, server_id):
        self = cls(server_id)
        self.refresh()


    def refresh(self):
        task_level_ids = {
            lv: ConfigTask.filter(level=lv).keys()
            for lv in range(1, ConfigBuilding.get(TASK_CENTRE_ID).max_levels+1)
            }

        levels = {}
        task_center = ConfigBuilding.get(TASK_CENTRE_ID)
        for i in range(1, task_center.max_levels+1):
            task_num = task_center.get_level(i).value1

            try:
                task_ids = random.sample(task_level_ids[i], task_num)
            except ValueError:
                task_ids = task_level_ids[i]

            levels[str(i)] = task_ids

        Common.set(self.server_id, MONGO_COMMON_KEY_TASK, levels)


    def get_task_ids(self, building_level):
        def get():
            doc = Common.get(self.server_id, MONGO_COMMON_KEY_TASK)

            if not doc:
                return []

            return doc.get(str(building_level), [])

        task_ids = get()
        if not task_ids:
            self.refresh()

        task_ids = get()
        if not task_ids:
            raise RuntimeError("can not get task.common for building_level {0}".format(building_level))

        return task_ids



class TaskManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = get_mongo_db(self.server_id)

        doc = self.mongo.task.find_one({'_id': self.char_id}, {'_id': 1})
        if not doc:
            self.refresh()

    @classmethod
    def clean(cls, server_id):
        mongo = get_mongo_db(server_id)
        mongo.task.drop()

    def receive(self, task_id):
        config = ConfigTask.get(task_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id('TASK_NOT_EXIST'))

        if BuildingManager(self.server_id, self.char_id).get_level(TASK_CENTRE_ID) < config.level:
            raise GameException(ConfigErrorMessage.get_error_id('BUILDING_TASK_CENTER_LEVEL_NOT_ENOUGH'))

        task = self.mongo.task.find_one(
            {'_id': self.char_id},
            {'tasks.{0}'.format(task_id): 1}
        )

        try:
            this_task = task['tasks'][str(task_id)]
        except KeyError:
            raise GameException(ConfigErrorMessage.get_error_id("TASK_NOT_FIND"))

        print "this_task =", this_task

        if this_task['status'] != TASK_STATUS_UNRECEIVED:
            raise GameException(ConfigErrorMessage.get_error_id("TASK_ALREADY_DOING"))


        doc = Document.get("task.char.embedded")
        doc['status'] = TASK_STATUS_DOING

        self.mongo.task.update_one(
            {'_id': self.char_id},
            {'$set': {'tasks.{0}'.format(task_id): doc}}
        )
        self.send_notify(ACT_UPDATE, [task_id])

    def get_reward(self, task_id):
        # check task finish
        task = self.mongo.task.find_one({'_id': self.char_id}, {'tasks.{0}'.format(task_id): 1})

        this_task = task['tasks'].get(str(task_id), None)
        if not this_task:
            raise GameException(ConfigErrorMessage.get_error_id("TASK_NOT_EXIST"))

        if this_task['status'] == TASK_STATUS_DOING:
            raise GameException(ConfigErrorMessage.get_error_id("TASK_NOT_DONE"))

        if this_task['status'] == TASK_STATUS_END:
            raise GameException(ConfigErrorMessage.get_error_id("TASK_ALREADY_GET_REWARD"))

        config = ConfigTask.get(task_id)
        Resource(self.server_id, self.char_id).add_from_package_id(config.package)
        self.mongo.task.update_one(
            {'_id': self.char_id},
            {'$set': {'tasks.{0}.status'.format(task_id): TASK_STATUS_END}}
        )

        self.send_notify(ACT_UPDATE, [task_id])

    def send_notify(self, act=ACT_INIT, task_ids=None):
        if not task_ids:
            projection = {'tasks': 1}
        else:
            projection = {'tasks.{0}'.format(i): 1 for i in task_ids}

        data = self.mongo.task.find_one({'_id': self.char_id}, projection)
        tasks = data.get('tasks', {})

        notify = TaskNotify()
        notify.act = act
        for k, v in tasks.iteritems():
            s = notify.task.add()
            s.id = int(k)
            s.num = v['num']
            s.status = v['status']

        MessagePipe(self.char_id).put(msg=notify)

    def update(self, **kwargs):
        task_id = kwargs.get('task_id', 0)
        num = kwargs.get('num', 0)

        task = self.mongo.task.find_one({'_id': self.char_id}, {'tasks.{0}'.format(task_id): 1})
        if task['tasks'].get(str(task_id), {}).get('status', None) != TASK_STATUS_DOING:
            return

        num += task['tasks'][str(task_id)]['num']
        updater = {'tasks.{0}.num'.format(task_id): num}

        config = ConfigTask.get(task_id)
        if num >= config.num:
            updater['tasks.{0}.status'.format(task_id)] = TASK_STATUS_FINISH

        self.mongo.task.update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_notify(ACT_UPDATE, [task_id])


    def refresh(self):
        task_doc = Document.get("task.char")
        task_doc['_id'] = self.char_id

        level = BuildingManager(self.server_id, self.char_id).get_level(TASK_CENTRE_ID)
        task_ids = TaskRefresh(self.server_id).get_task_ids(level)

        new_tasks_doc = Document.get("task.char.embedded")
        new_tasks_doc['status'] = TASK_STATUS_UNRECEIVED

        new_tasks = {str(task_id): new_tasks_doc for task_id in task_ids}

        self.mongo.task.update_one(
            {'_id': self.char_id},
            {'$set': {'tasks': new_tasks}},
            upsert=True
        )

        return task_ids
