__author__ = 'hikaly'

# -*- coding:utf-8 -*-

from core.db import get_mongo_db
from config.task import ConfigTask
from config import ConfigErrorMessage
from core.resource import Resource
from dianjing.exception import GameException
from protomsg.task_pb2 import TaskNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from utils.message import MessagePipe

TASK_STATUS_UNRECEIVED = 0
TASK_STATUS_DOING = 1
TASK_STATUS_FINISH = 2
TASK_STATUS_END = 3

class TaskRefresh(object):
    def __init__(self, server_id):
        self.server = server_id
        self.mongo = get_mongo_db(server_id)
        data = self.mongo.common.find_one({'_id': 'task'}, {'tasks': 1})
        if not data:
            doc = {
                '_id': 'task',
                'tasks': [],
            }
            self.mongo.common.insert_one(doc)


    def task_refresh(self):
        pass




class TaskManage(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = get_mongo_db(self.server_id)

        data = self.mongo.task.find_one({'_id': self.char_id})
        if not data:
            doc = {'_id': self.char_id, 'tasks': {}}
            self.mongo.task.insert_one(doc)


    def receive(self, task_id):
        task = ConfigTask.get(task_id)
        if not task:
            raise GameException(ConfigErrorMessage.get_error_id('TASK_NOT_EXIST'))

        club = self.mongo.character.find_on({'_id': self.char_id}, {'club': 1})
        if club['club']['level'] < task.level:
            raise GameException(ConfigErrorMessage.get_error_id('CLUB_LEVEL_NOT_ENOUGH'))

        doc = {
            'num': 0,
            'status': TASK_STATUS_DOING,
        }
        self.mongo.task.update(
            {'_id': self.char_id},
            {'$set': {'tasks.{0}'.format(task_id): doc}}
        )
        self.send_notify(ACT_UPDATE, [task_id])


    def get_reward(self, task_id):

        # TODO check task finish
        task = self.mongo.task.find_one({'_id': self.char_id}, {'tasks.{0}'.format(task_id): 1})
        if task['tasks'][str(task_id)]['status'] != 2:
            raise GameException(ConfigErrorMessage.get_error_id('TASK_NOT_FINISH'))
        # TODO add rewarded
        config = ConfigTask.get(task_id)

        Resource(self.server_id, self.char_id).add_from_package_id(config['package'])
        self.mongo.task.update(
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
            s = notify.tasks.add()
            s.id = int(k)
            s.num = v['num']
            s.status = v['status']

        MessagePipe(self.char_id).put(msg=notify)


    def update(self, **kwargs):
        task_id = kwargs.get('id', 0)
        num = kwargs.get('num', 0)
        task = self.mongo.task.find_one({'_id': self.char_id}, {'tasks.{0}'.format(task_id): 1})
        num += task['tasks'][str(task_id)]['num']

        # Tips//status: 0==received  1==finished  2==rewarded
        config = ConfigTask.get(task_id)
        if num >= config['num']:
            num = config['num']
            self.mongo.task.update(
                {'_id': self.char_id},
                {'$set': {'tasks.{0}.status'.format(task_id): TASK_STATUS_FINISH}}
            )

        self.mongo.task.update(
            {'_id': self.char_id},
            {'$set': {'tasks.{0}.num'.format(task_id): num}}
        )

        self.send_notify(ACT_UPDATE, [task_id])


    def clear(self):
        # TODO clear task data
        self.mongo.task.delete_one({'_id': self.char_id})

    def refresh(self):
        pass




