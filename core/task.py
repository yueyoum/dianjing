__author__ = 'hikaly'

# -*- coding:utf-8 -*-

from core.db import get_mongo_db

from config.task import ConfigTask

TaskStatus = {'unreceived', 'received', 'finish', 'get_reward'}

class TaskManage(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = get_mongo_db(self.server_id)

        data = self.mongo.task.find_one({'_id': self.char_id}, {'task': 1})
        if not data:
            doc = {'_id', 'task_id', 'progress', 'statue'}
            doc['_id'] = self.char_id
            doc['task_id'] = 1
            doc['progress'] = None
            doc['status'] = TaskStatus[0]
            self.mongo.task.insert_one(doc)

    def task_process_mark(self, id, num):
        pass

    def send_notify(self):
        #msg = self.make_protomsg()
        #notify = ClubNotify()
        #notify.club.MergeFrom(msg)
        #MessagePipe(self.char_id).put(notify)
        pass

    def get_reward(self):
        pass

    def update(self):
        pass
