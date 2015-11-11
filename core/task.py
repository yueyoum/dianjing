# -*- coding:utf-8 -*-


from dianjing.exception import GameException

from core.mongo import MongoTask, MongoRecord
from core.package import Drop
from core.resource import Resource
from core.signals import random_event_done_signal

from config import ConfigErrorMessage, ConfigTask, ConfigRandomEvent

from utils.message import MessagePipe, MessageFactory

from protomsg.task_pb2 import TaskNotify, RandomEventNotify, TASK_DOING, TASK_FINISH
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE

TASK_STATUS_DOING = 1
TASK_STATUS_FINISH = 2

MAIN_TASK = 1
BRANCH_TASK = 2
DAILY_TASK = 3


def is_daily_task(task_id):
    return ConfigTask.get(task_id).tp == DAILY_TASK


class TaskManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoTask.exist(self.server_id, self.char_id):
            doc = MongoTask.document()
            doc['_id'] = self.char_id
            MongoTask.db(self.server_id).insert_one(doc)

            self.refresh()

    def refresh(self):
        self.clean_daily()

        new_doc = {}
        task_ids = ConfigTask.filter(tp=DAILY_TASK, task_begin=True)
        for task_id in task_ids.keys():
            new_doc['doing.{0}'.format(task_id)] = {}

        MongoTask.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': new_doc},
        )

    def add_task(self, task_id):
        config = ConfigTask.get(task_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id('TASK_NOT_EXIST'))

        MongoTask.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'doing.{0}'.format(task_id): {}}}
        )

        self.send_notify(ids=[task_id])

    def get_reward(self, task_id):
        config = ConfigTask.get(task_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("TASK_NOT_EXIST"))

        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'finish': 1})
        if task_id not in doc['finish']:
            raise GameException(ConfigErrorMessage.get_error_id("TASK_NOT_DONE"))

        drop = Drop.generate(config.package)
        message = u"Reward from task {0}".format(task_id)
        Resource(self.server_id, self.char_id).save_drop(drop, message=message)

        if not is_daily_task(task_id):
            MongoTask.db(self.server_id).update_one(
                {'_id': self.char_id},
                {
                    '$push': {'history': task_id},
                    '$pull': {'finish': task_id}
                }
            )
        else:
            MongoTask.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$pull': {'finish': task_id}}
            )

        if config.next_task:
            self.add_task(config.next_task)

        self.send_notify(ids=[task_id])
        return drop.make_protomsg()

    # def finish(self, task_id):
    #     MongoTask.db(self.server_id).update_one(
    #         {'_id': self.char_id},
    #         {
    #             '$unset': {'doing.{0}'.format(task_id): ''},
    #             '$push': {'finish': task_id}
    #         }
    #     )

    def trig_by_tp(self, trigger, num):
        # 按照类型来触发
        task_ids = ConfigTask.filter(trigger=trigger)
        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'history': 1})

        # 没做过, 条件值满足, add
        for task_id in task_ids:
            config = ConfigTask.get(task_id)

            if config.trigger_value <= num and config.id not in doc['history']:
                self.add_task(task_id)

    def clean_daily(self):
        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'history': 0})

        doing_ids = doc['doing'].keys()
        finish_ids = doc['finish']

        daily_doing_updater = {}
        for i in doing_ids:
            if is_daily_task(i):
                daily_doing_updater['doing.{0}'.format(i)] = 1

        daily_finish_updater = []
        for i in finish_ids:
            if is_daily_task(i):
                daily_finish_updater.append(i)

        if daily_doing_updater or daily_finish_updater:
            MongoTask.db(self.server_id).update_one(
                {'_id': self.char_id},
                {
                    '$unset': daily_doing_updater,
                    '$pullAll': daily_finish_updater
                }
            )

            self.send_notify()

    def update(self, target_id, num):
        docs = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'doing': 1})

        for k, v in docs['doing']:
            if target_id in v.keys():
                config = ConfigTask.get(int(k))
                if v[str(target_id)] + num > config.targets[target_id]:
                    v[str(target_id)] = config.targets[target_id]
        self.finish()

    def finish(self):
        docs = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'doing': 1})

        unsetter = {}
        projection = {}
        for k, v in docs['doing'].iteritems():
            config = ConfigTask.get(int(k))
            finish = True
            setter = {}
            for target_id, value in v.iteritems():
                if config.targets[target_id] > value:
                    finish = False
                    break
                setter[str(target_id)] = config.targets[target_id]

            if finish:
                unsetter['doing.{0}'.format(k)] = ''
                projection['finish.{0}'.format(k)] = setter

        MongoTask.db(self.server_id).update_one(
            {'_id': 1},
            {
                '$unset': unsetter,
                '$set': projection,
            }
        )

    def trig_by_id(self, task_id, num):
        # 按照任务ID来触发
        # 目前只用于客户端触发的任务，比如点击NPC
        config = ConfigTask.get(task_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("TASK_NOT_EXIST"))

        if not config.client_task:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        doc = MongoTask.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'tasks.{0}'.format(task_id): 1}
        )

        try:
            this_task = doc['tasks'][str(task_id)]
        except KeyError:
            return

        if this_task['status'] != TASK_STATUS_DOING:
            return

        updater = {}
        new_num = this_task['num'] + num
        updater['tasks.{0}.num'.format(task_id)] = new_num
        if new_num >= config.trigger_value:
            updater['tasks.{0}.status'.format(task_id)] = TASK_STATUS_FINISH

        MongoTask.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_notify(ids=[task_id])

    def send_notify(self, ids=None):
        if not ids:
            act = ACT_INIT
        else:
            act = ACT_UPDATE

        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'history': 0})

        notify = TaskNotify()
        notify.act = act

        for k, v in doc['doing'].iteritems():
            notify_task = notify.task.add()
            notify_task.id = int(k)
            notify_task.status = TASK_DOING

            for target_id, target_value in ConfigTask.get(int(k)).targets.iteritems():
                notify_task_target = notify_task.targets.add()
                notify_task_target.id = target_id
                notify_task_target.value = v.get(str(target_id), 0)

        for k in doc['finish']:
            notify_task = notify.task.add()
            notify_task.id = k
            notify_task.status = TASK_FINISH

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

        # TODO filter chars
        notify = RandomEventNotify()
        notify.times = 0
        data = MessageFactory.pack(notify)

        from core.mongo import MongoCharacter
        for char in MongoCharacter.db(server_id).find():
            char_id = char['_id']
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

        drop = Drop.generate(config.package)
        message = u"RandomEvent Done. {0}".format(event_id)
        Resource(self.server_id, self.char_id).save_drop(drop, message)

        MongoRecord.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {
                'records.{0}'.format(self.KEY): 1
            }}
        )

        self.send_notify()
        return drop.make_protomsg()

    def send_notify(self):
        doc = MongoRecord.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'records.{0}'.format(self.KEY): 1}
        )

        notify = RandomEventNotify()
        notify.times = doc['records'].get(self.KEY, 0)
        MessagePipe(self.char_id).put(msg=notify)
