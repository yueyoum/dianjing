# -*- coding:utf-8 -*-


from dianjing.exception import GameException

from core.mongo import MongoTaskMain, MongoRecord
from core.character import Character
from core.resource import ResourceClassification
from core.signals import random_event_done_signal, daily_task_finish_signal

from config import ConfigErrorMessage, ConfigRandomEvent, ConfigTaskMain

from utils.message import MessagePipe, MessageFactory

from protomsg.task_pb2 import TaskNotify, RandomEventNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE


MAX_TASK_MAIN_ID = max(ConfigTaskMain.INSTANCES.keys())

class TaskMain(object):
    __slots__ = ['server_id', 'char_id', 'doing']
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        doc = MongoTaskMain.db(self.server_id).find_one({'_id': self.char_id})
        if doc:
            self.doing = doc['doing']
        else:
            doc = MongoTaskMain.document()
            doc['_id'] = self.char_id
            MongoTaskMain.db(self.server_id).insert_one(doc)

            self.doing = 1


    def trig(self, challenge_id):
        if not self.doing:
            # 任务都做完了
            return

        config = ConfigTaskMain.get(self.doing)
        if challenge_id < config.challenge_id:
            return

        if self.doing >= MAX_TASK_MAIN_ID:
            self.doing = 0
        else:
            self.doing += 1

        MongoTaskMain.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'doing': self.doing
            }}
        )

        resource_classified = ResourceClassification.classify(config.items)
        resource_classified.add(self.server_id, self.char_id)

        self.send_notify(update=True)

    def send_notify(self, update=False):
        notify = TaskNotify()
        if update:
            notify.act = ACT_UPDATE
        else:
            notify.act = ACT_INIT

        notify.doing = self.doing

        MessagePipe(self.char_id).put(msg=notify)




class RandomEvent(object):
    KEY = 'random_events'

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoRecord.exist(self.server_id, self.char_id):
            doc = MongoRecord.document()
            doc['_id'] = self.char_id
            MongoRecord.db(self.server_id).insert_one(doc)

    @classmethod
    def cronjob(cls, server_id):
        MongoRecord.db(server_id).update_many(
            {},
            {'$unset': {
                'records.{0}'.format(cls.KEY): 1
            }}
        )

        notify = RandomEventNotify()
        notify.times = 0
        data = MessageFactory.pack(notify)

        for char_id in Character.get_recent_login_char_ids(server_id):
            MessagePipe(char_id).put(data=data)

    def done(self, event_id):
        config = ConfigRandomEvent.get(event_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        random_event_done_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            event_id=event_id
        )

        # drop = Drop.generate(config.package)
        # message = u"RandomEvent Done. {0}".format(event_id)
        # Resource(self.server_id, self.char_id).save_drop(drop, message)
        #
        # MongoRecord.db(self.server_id).update_one(
        #     {'_id': self.char_id},
        #     {'$inc': {
        #         'records.{0}'.format(self.KEY): 1
        #     }}
        # )
        #
        # self.send_notify()
        # return drop.make_protomsg()

    def send_notify(self):
        doc = MongoRecord.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'records.{0}'.format(self.KEY): 1}
        )

        notify = RandomEventNotify()
        notify.times = doc['records'].get(self.KEY, 0)
        MessagePipe(self.char_id).put(msg=notify)
