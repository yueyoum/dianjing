# -*- coding:utf-8 -*-


from dianjing.exception import GameException

from core.mongo import MongoTask, MongoRecord
from core.character import Character
from core.package import Drop
from core.resource import Resource
from core.signals import random_event_done_signal, daily_task_finish_signal

from config import ConfigErrorMessage, ConfigTask, ConfigRandomEvent, ConfigTaskTargetType

from utils.message import MessagePipe, MessageFactory

from protomsg.task_pb2 import TaskNotify, TaskRemoveNotify, RandomEventNotify, TASK_DOING, TASK_FINISH
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE

# task status
TASK_STATUS_DOING = 1
TASK_STATUS_FINISH = 2

# task branch
MAIN_TASK = 1
BRANCH_TASK = 2
DAILY_TASK = 3


def get_target_current_value(server_id, char_id, target_id, param, task_data):
    config = ConfigTaskTargetType.get(target_id)
    if config.mode == 1:
        key = '{0}:{1}'.format(target_id, param)
        return task_data.get(key, 0)

    module, class_name, func_name = config.compare_source.rsplit('.', 2)
    module = __import__(module, fromlist=[class_name], level=0)
    Cls = getattr(module, class_name)
    obj = Cls(server_id, char_id)

    func = getattr(obj, func_name)
    if config.has_param:
        return func(param)
    else:
        return func()


class TaskManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoTask.exist(self.server_id, self.char_id):
            doc = MongoTask.document()
            doc['_id'] = self.char_id

            # 初始化主线 和 日常
            doing = {}
            for tid in ConfigTask.HEAD_TASKS:
                config = ConfigTask.get(tid)
                if config.is_daily_task() or config.is_main_task():
                    doing[str(tid)] = {}

            doc['doing'] = doing
            MongoTask.db(self.server_id).insert_one(doc)

    @classmethod
    def cronjob(cls, server_id):
        char_ids = Character.get_recent_login_char_ids(server_id)
        for cid in char_ids:
            cls(server_id, cid).refresh()

    def refresh(self):
        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'history': 0})

        doing_ids = doc['doing'].keys()
        finish_ids = doc['finish']

        daily_doing_updater = {}
        for i in doing_ids:
            if ConfigTask.get(i).is_daily_task():
                daily_doing_updater['doing.{0}'.format(i)] = 1

        daily_finish_updater = []
        for i in finish_ids:
            if ConfigTask.get(i).is_daily_task():
                daily_finish_updater.append(i)

        if daily_doing_updater or daily_finish_updater:
            MongoTask.db(self.server_id).update_one(
                {'_id': self.char_id},
                {
                    '$unset': daily_doing_updater,
                    '$pullAll': {'finish': daily_finish_updater}
                }
            )

        updater = {}
        task_ids = ConfigTask.filter(tp=DAILY_TASK, task_begin=True)
        for tid in task_ids.keys():
            updater['doing.{0}'.format(tid)] = {}

        MongoTask.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater},
        )

        self.send_notify()

    def add_task(self, task_id):
        config = ConfigTask.get(task_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id('TASK_NOT_EXIST'))

        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id})
        if str(task_id) in doc['doing'] or task_id in doc['finish'] or task_id in doc['history']:
            return

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

        if not config.is_daily_task():
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
            self.send_remove_notify(task_id)
            self.add_task(config.next_task)

        return drop.make_protomsg()

    def trigger(self, trigger, num):
        # 按照类型来触发
        task_ids = ConfigTask.filter(trigger=trigger).keys()
        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id})

        doing_ids = [int(i) for i in doc['doing'].keys()]
        doc_task_ids = set(doc['history']) | set(doc['finish']) | set(doing_ids)
        # 没做过, 条件值满足, add
        for task_id in task_ids:
            config = ConfigTask.get(task_id)

            # TODO, 更完备的判断
            if config.trigger_value <= num and config.id not in doc_task_ids:
                self.add_task(task_id)

    def update(self, target_id, param, value):
        task_ids = ConfigTask.TARGET_TASKS.get(target_id, [])
        if not task_ids:
            return

        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'doing': 1})
        config_target = ConfigTaskTargetType.get(target_id)

        updater = {}
        target_key = (target_id, param)

        for task_id in task_ids:
            if str(task_id) not in doc['doing']:
                continue

            config_task = ConfigTask.get(int(task_id))
            if config_target.mode == 1:

                expected_value = config_task.targets[target_key]
                target_value = get_target_current_value(self.server_id, self.char_id, target_id, param,
                                                        doc['doing'][str(task_id)])
                target_value += value

                if target_value > expected_value:
                    target_value = expected_value

                updater['doing.{0}.{1}:{2}'.format(task_id, target_id, param)] = target_value

        if updater:
            MongoTask.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': updater},
            )

        self.finish(task_ids)

    def finish(self, task_ids):
        docs = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'doing': 1})

        unsetter = {}
        finish_ids = []

        for tid in task_ids:
            task_data = docs['doing'].get(str(tid), {})
            if not task_data:
                continue

            config_task = ConfigTask.get(tid)

            for target_key, expected_value in config_task.targets.iteritems():
                target_id, param = target_key

                config_target = ConfigTaskTargetType.get(target_id)
                current_value = get_target_current_value(self.server_id, self.char_id, target_id, param, task_data)

                if config_target.compare_type == 1:
                    if not current_value >= expected_value:
                        break
                else:
                    if not current_value <= expected_value:
                        break
            else:
                # finish
                unsetter['doing.{0}'.format(tid)] = 1
                finish_ids.append(tid)

        if unsetter:
            MongoTask.db(self.server_id).update_one(
                {'_id': self.char_id},
                {
                    '$unset': unsetter,
                    '$push': {'finish': {'$each': finish_ids}},
                },
            )

        for k in finish_ids:
            if ConfigTask.get(k).is_daily_task():
                daily_task_finish_signal.send(
                    sender=None,
                    server_id=self.server_id,
                    char_id=self.char_id,
                    task_id=k,
                )

        self.send_notify(ids=task_ids)

    def trig_by_id(self, task_id):
        # 按照任务ID来触发
        # 目前只用于客户端触发的任务，比如点击NPC
        config = ConfigTask.get(task_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("TASK_NOT_EXIST"))

        if not config.client_task:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        for target_key, expected_value in config.targets.iteritems():
            target_id, param = target_key
            self.update(target_id, param, expected_value)

    def send_remove_notify(self, _id):
        notify = TaskRemoveNotify()
        notify.id = _id
        MessagePipe(self.char_id).put(msg=notify)

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

            for target_id, target_conf in ConfigTask.get(int(k)).targets.iteritems():
                notify_task_target = notify_task.targets.add()
                notify_task_target.id = target_id
                notify_task_target.param = target_conf[0]
                notify_task_target.current_value = get_target_current_value(self.server_id, self.char_id, target_id,
                                                                            target_conf[0], v)

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
