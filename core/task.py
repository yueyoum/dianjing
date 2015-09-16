# -*- coding:utf-8 -*-

import random

from dianjing.exception import GameException

from core.mongo import MongoTask
from core.package import Drop
from core.resource import Resource
from core.building import BuildingTaskCenter
from core.common import CommonTask

from config import ConfigErrorMessage, ConfigTask, ConfigBuilding

from utils.message import MessagePipe

from protomsg.task_pb2 import TaskNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE

TASK_STATUS_UNRECEIVED = 0
TASK_STATUS_DOING = 1
TASK_STATUS_FINISH = 2
TASK_STATUS_END = 3


class TaskRefresh(object):
    def __init__(self, server_id):
        self.server_id = server_id

    @classmethod
    def cron_job(cls, server_id):
        self = cls(server_id)
        self.refresh()

    def refresh(self):
        task_center = ConfigBuilding.get(BuildingTaskCenter.BUILDING_ID)

        levels = {}
        for i in range(1, task_center.max_levels + 1):
            this_level_task_ids = ConfigTask.filter(level=i).keys()
            task_num = task_center.get_level(i).value1

            try:
                task_ids = random.sample(this_level_task_ids, task_num)
            except ValueError:
                task_ids = this_level_task_ids

            levels[str(i)] = task_ids

        CommonTask.set(self.server_id, levels)

    def get_task_ids(self, building_level):
        def get():
            value = CommonTask.get(self.server_id)

            if not value:
                return []

            return value.get(str(building_level), [])

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

        if not MongoTask.exist(server_id, self.char_id):
            self.refresh()

    @classmethod
    def clean(cls, server_id):
        MongoTask.db(server_id).drop()

    def refresh(self):
        task_doc = MongoTask.document()
        task_doc['_id'] = self.char_id

        level = BuildingTaskCenter(self.server_id, self.char_id).get_level()
        task_ids = TaskRefresh(self.server_id).get_task_ids(level)

        new_tasks_doc = MongoTask.document_task()
        new_tasks_doc['status'] = TASK_STATUS_UNRECEIVED

        new_tasks = {str(task_id): new_tasks_doc for task_id in task_ids}

        MongoTask.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'tasks': new_tasks}},
            upsert=True
        )

        return task_ids

    def receive(self, task_id):
        config = ConfigTask.get(task_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id('TASK_NOT_EXIST'))

        if BuildingTaskCenter(self.server_id, self.char_id).get_level() < config.level:
            raise GameException(ConfigErrorMessage.get_error_id('BUILDING_TASK_CENTER_LEVEL_NOT_ENOUGH'))

        doc = MongoTask.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'tasks.{0}'.format(task_id): 1}
        )

        try:
            this_task = doc['tasks'][str(task_id)]
        except KeyError:
            raise GameException(ConfigErrorMessage.get_error_id("TASK_NOT_FIND"))

        if this_task['status'] != TASK_STATUS_UNRECEIVED:
            raise GameException(ConfigErrorMessage.get_error_id("TASK_ALREADY_DOING"))

        MongoTask.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'tasks.{0}.status'.format(task_id): TASK_STATUS_DOING}}
        )

        self.send_notify(ids=[task_id])

    def get_reward(self, task_id):
        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'tasks.{0}'.format(task_id): 1})

        this_task = doc['tasks'].get(str(task_id), None)
        if not this_task:
            raise GameException(ConfigErrorMessage.get_error_id("TASK_NOT_EXIST"))

        if this_task['status'] == TASK_STATUS_UNRECEIVED or this_task['status'] == TASK_STATUS_DOING:
            raise GameException(ConfigErrorMessage.get_error_id("TASK_NOT_DONE"))

        if this_task['status'] == TASK_STATUS_END:
            raise GameException(ConfigErrorMessage.get_error_id("TASK_ALREADY_GET_REWARD"))

        config = ConfigTask.get(task_id)
        drop = Drop.generate(config.package)
        message = u"Reward from task {0}".format(task_id)
        Resource(self.server_id, self.char_id).save_drop(drop, message=message)
        MongoTask.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'tasks.{0}.status'.format(task_id): TASK_STATUS_END}}
        )

        self.send_notify(ids=[task_id])

    def trig(self, tp, num):
        # 按照类型来触发
        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'tasks': 1})
        tasks = doc['tasks']

        updated_ids = []
        updater = {}

        for k, v in tasks.iteritems():
            config = ConfigTask.get(int(k))
            if config.tp != tp:
                continue

            if v['status'] != TASK_STATUS_DOING:
                continue

            updated_ids.append(k)
            # TODO 是否有其他类型的判断
            new_num = v['num'] + num
            updater['tasks.{0}.num'.format(k)] = new_num
            if new_num >= config.num:
                updater['tasks.{0}.status'.format(k)] = TASK_STATUS_FINISH

        if updated_ids:
            MongoTask.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': updater}
            )

            self.send_notify(ids=updated_ids)

    def send_notify(self, ids=None):
        if not ids:
            projection = {'tasks': 1}
            act = ACT_INIT
        else:
            projection = {'tasks.{0}'.format(i): 1 for i in ids}
            act = ACT_UPDATE

        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, projection)
        tasks = doc.get('tasks', {})

        notify = TaskNotify()
        notify.act = act
        for k, v in tasks.iteritems():
            s = notify.task.add()
            s.id = int(k)
            s.num = v['num']
            s.status = v['status']

        MessagePipe(self.char_id).put(msg=notify)
