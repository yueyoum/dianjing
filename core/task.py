# -*- coding:utf-8 -*-


from dianjing.exception import GameException

from core.mongo import MongoTaskMain, MongoRecord, MongoTaskDaily
from core.character import Character
from core.resource import ResourceClassification
from core.club import get_club_property
from core.vip import VIP
from core.signals import random_event_done_signal, daily_task_finish_signal

import core.value_log as VLOG

from config import ConfigErrorMessage, ConfigRandomEvent, ConfigTaskMain, ConfigTaskDaily, ConfigTaskCondition

from utils.message import MessagePipe, MessageFactory

from protomsg.task_pb2 import TaskNotify, RandomEventNotify, TaskDailyNotify, TASK_DOING, TASK_DONE, TASK_FINISH
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



def get_task_condition_value(server_id, char_id, condition_id):
    config = ConfigTaskCondition.get(condition_id)
    if not config or not config.server_module:
        # TODO
        return 0

    CLS = getattr(VLOG, config.server_module)
    obj = CLS(server_id, char_id)
    """:type: core.value_log.ValueLog"""

    return obj.count_of_today()


class TaskDaily(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.doc = MongoTaskDaily.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoTaskDaily.document()
            self.doc['_id'] = self.char_id
            self.doc['tasks'] = self.refresh()
            MongoTaskDaily.db(self.server_id).insert_one(self.doc)

    def refresh(self):
        club_level = get_club_property(self.server_id, self.char_id, 'level')
        vip_level = VIP(self.server_id, self.char_id).level

        task_ids = []
        for k, v in ConfigTaskDaily.INSTANCES.iteritems():
            if club_level < v.club_level:
                continue

            if vip_level < v.vip_level:
                continue

            task_ids.append(k)

        return task_ids

    def try_open(self):
        task_ids = self.refresh()
        new_task_ids = []
        for i in task_ids:
            if i not in self.doc['done'] and i not in self.doc['tasks']:
                self.doc['tasks'].append(i)
                new_task_ids.append(i)

        MongoTaskDaily.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'tasks': self.doc['tasks']
            }}
        )

        self.send_notify(task_ids=new_task_ids)

    def trig(self, condition_id):
        task_ids = ConfigTaskDaily.get_task_ids_by_condition_id(condition_id)
        doing_task_ids = [i for i in task_ids if i in self.doc['tasks']]
        self.send_notify(task_ids=doing_task_ids)

    def get_task_status(self, task_id):
        """

        :rtype: (int, int)
        """
        config = ConfigTaskDaily.get(task_id)
        current_value = get_task_condition_value(self.server_id, self.char_id, config.condition_id)

        if task_id in self.doc['done']:
            return current_value, TASK_DONE

        if task_id not in self.doc['tasks']:
            return None, None

        # TODO 注意其他比较方式
        if current_value >= config.condition_value:
            return current_value, TASK_FINISH

        return current_value, TASK_DOING

    def get_reward(self, task_id):
        config = ConfigTaskDaily.get(task_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        _, status = self.get_task_status(task_id)
        if status == TASK_DONE:
            raise GameException(ConfigErrorMessage.get_error_id("TASK_GET_REWARD_ALREADY_GOT"))

        if status != TASK_FINISH:
            raise GameException(ConfigErrorMessage.get_error_id("TASK_GET_REWARD_NOT_FINISH"))

        self.doc['tasks'].remove(task_id)
        self.doc['done'].append(task_id)

        resource_classified = ResourceClassification.classify(config.rewards)
        resource_classified.add(self.server_id, self.char_id)

        MongoTaskDaily.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'tasks': self.doc['tasks'],
                'done': self.doc['done'],
            }}
        )

        self.send_notify(task_ids=[task_id])

        return resource_classified

    def send_notify(self, task_ids=None):
        if task_ids:
            act = ACT_UPDATE
        else:
            act = ACT_INIT
            task_ids = self.doc['tasks']

        notify = TaskDailyNotify()
        notify.act = act
        for tid in task_ids:
            current_value, status = self.get_task_status(tid)

            notify_task = notify.tasks.add()
            notify_task.id = tid
            notify_task.value = current_value
            notify_task.status = status

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
