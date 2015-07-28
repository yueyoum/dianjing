__author__ = 'hikaly'

# -*- coding:utf-8 -*-

from core.db import get_mongo_db
from config.task import ConfigTask
from config import ConfigErrorMessage
from core.resource import Resource
from dianjing.exception import GameException


class TaskManage(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = get_mongo_db(self.server_id)

        data = self.mongo.task.find_one({'_id': self.char_id})
        if not data:
            doc = {'_id': None, 'received': {}, 'finished': [], 'rewarded': []}
            self.mongo.task.insert_one(doc)


    def receive(self, task_id):
        task = ConfigTask.get(task_id)
        if not task:
            raise GameException(ConfigErrorMessage.get_error_id('TASK_NOT_EXIST'))

        club = self.mongo.character.find_on({'_id': self.char_id}, {'club': 1})
        if club['level'] < task.level:
            raise GameException(ConfigErrorMessage.get_error_id('CLUB_LEVEL_NOT_ENOUGH'))

        doc = {'{0}'.format(task_id): 0}
        self.mongo.task.update(
            {'_id': self.char_id},
            {'$set': {'received.{0}'.format(task_id): doc}}
        )


    def get_reward(self, task_id):
        # TODO check if in finished list
        finished = self.mongo.task.find_one({'_id': self.char_id}, {'finished': 1})
        if task_id not in finished['finished']:
            raise GameException(ConfigErrorMessage.get_error_id('FINISH_TASK_NOT_FOUND'))
        # TODO add rewarded
        config = ConfigTask.get(task_id)
        package_id = config['task']['reward']
        Resource(self.server_id, self.char_id).add_from_package_id(package_id)

        finished['finished'].remove(task_id)
        self.mongo.task.update(
            {'_id': self.char_id},
            {'$set': {'finished': finished['finished']}}
        )

        rewarded = self.mongo.task.find_one({'_id': self.char_id}, {'rewarded': 1})
        rewarded['rewarded'].append(task_id)
        self.mongo.task.update(
            {'_id': self.char_id},
            {'$set': {'rewarded': rewarded['rewarded']}}
        )


    def send_notify(self):
        pass


    def update(self, **kwargs):
        task_id = kwargs.get('id', 0)
        doc = {
            'num': kwargs.get('num'),
        }
        data = self.mongo.task.find_one({'_id': self.char_id}, {'received.{0}'.format(task_id): 1})
        doc['num'] += data['received']['{0}'.format(task_id)]['num']

        # Tips//status: 0==received  1==finished  2==rewarded
        if self._check_finish(task_id, doc['num']):
            finished = self.mongo.task.find_one({'_id': self.char_id}, {'finished': 1})
            finished['finished'].append(doc['id'])
            self.mongo.task.update(
                {'_id': self.char_id},
                {'$set': {'finished': finished['finished']}}
            )

            received = self.mongo.task.find_one({'_id': self.char_id}, {'received': 1})
            del received['received']['{0}'.format(task_id)]
            self.mongo.task.update(
                {'_id': self.char_id},
                {'$set': {'received': received['received']}}
            )
        else:
            self.mongo.task.update(
                {'_id': self.char_id},
                {'$set': {'received.{0}'.format(task_id): doc}}
            )


    def _check_finish(self, task_id, num):
        config = ConfigTask.get(task_id)
        if num >= config.task.num:
            return True
        return False


    def clear(self):
        # TODO clear task data
        self.mongo.task.delete_one({'_id': self.char_id})



