__author__ = 'hikaly'

# -*- coding:utf-8 -*-

from core.db import get_mongo_db
from config.task import ConfigTask
from config import CONFIG
from  dianjing.exception import GameException

TaskStatus = {'unreceived', 'received', 'finish', 'get_reward'}

class TaskManage(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = get_mongo_db(self.server_id)

        data = self.mongo.task.find_one({'_id': self.char_id}, {'task': 1})
        if not data:
            doc = {'_id', {'task_id', 'progress', 'statue'}}
            doc['_id'] = self.char_id
            doc['task_id'] = 1
            doc['progress'] = None
            doc['status'] = TaskStatus[0]
            self.mongo.task.insert_one(doc)

    def task_process_mark(self, task_id, num):
        self.mongo.update()

    def send_notify(self):
        pass

    def get_reward(self, task_id):
        pass

    def update(self):
        self.mongo.update()
        pass

    def check_task(self, task_id):
        # TODO check task config exist
        task_config = ConfigTask.get(task_id)
        if not task_config:
            raise False
        # TODO check task own
        data_club = self.mongo.character.find_one({'_id': self.char_id}, {'club': 1})
        if data_club['club'].level < task_config['level']:
            raise False
        return True

    def check_finish(self, task_id):
        self.mongo.task.find_one({'_id': self.char_id},     )

