# -*- coding:utf-8 -*-

from dianjing.exception import GameException

from core.mongo import MongoTaskMain, MongoTaskDaily
from core.resource import ResourceClassification
from core.club import get_club_property
from core.vip import VIP
from core.challenge import Challenge

from config import ConfigErrorMessage, ConfigTaskMain, ConfigTaskDaily, ConfigTaskCondition

from utils.message import MessagePipe
from utils.functional import get_start_time_of_today

from protomsg.task_pb2 import TaskNotify, TaskDailyNotify, TASK_DOING, TASK_DONE, TASK_FINISH
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE


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
        if not Challenge(self.server_id, self.char_id).is_challenge_id_passed(config.challenge_id):
            return

        if self.doing >= ConfigTaskMain.MAX_ID:
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
        resource_classified.add(self.server_id, self.char_id, message="TaskMain.trig:{0}".format(challenge_id))

        self.send_notify(update=True)

    def send_notify(self, update=False):
        notify = TaskNotify()
        if update:
            notify.act = ACT_UPDATE
        else:
            notify.act = ACT_INIT

        notify.doing = self.doing

        MessagePipe(self.char_id).put(msg=notify)


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
        passed_challenge_ids = Challenge(self.server_id, self.char_id).get_passed_challenge_ids()

        task_ids = []
        for k, v in ConfigTaskDaily.INSTANCES.iteritems():
            if club_level < v.club_level:
                continue

            if vip_level < v.vip_level:
                continue

            if v.challenge_id and v.challenge_id not in passed_challenge_ids:
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
        if not task_ids:
            return

        doing_task_ids = [i for i in task_ids if i in self.doc['tasks']]
        self.send_notify(task_ids=doing_task_ids)

    def get_task_status(self, task_id, start_at=None, end_at=None):
        """

        :rtype: (int, int)
        """

        if not start_at or not end_at:
            # 日常任务的的时间范围肯定就是当天了
            start_time = get_start_time_of_today()
            end_time = start_time.replace(days=1)

            start_at = start_time.timestamp
            end_at = end_time.timestamp

        config = ConfigTaskDaily.get(task_id)
        config_condition = ConfigTaskCondition.get(config.condition_id)
        if not config_condition:
            current_value = 0
        else:
            current_value = config_condition.get_value(self.server_id, self.char_id, start_at=start_at, end_at=end_at)

        if task_id in self.doc['done']:
            return current_value, TASK_DONE

        if task_id not in self.doc['tasks']:
            return None, None

        if config_condition.compare_value(self.server_id, self.char_id, current_value, config.condition_value):
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
        resource_classified.add(self.server_id, self.char_id, message="TaskDaily.get_reward:{0}".format(task_id))

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
        # 日常任务的的时间范围肯定就是当天了
        start_time = get_start_time_of_today()
        end_time = start_time.replace(days=1)

        start_at = start_time.timestamp
        end_at = end_time.timestamp

        if task_ids:
            act = ACT_UPDATE
        else:
            act = ACT_INIT
            task_ids = self.doc['tasks']

        notify = TaskDailyNotify()
        notify.act = act
        for tid in task_ids:
            current_value, status = self.get_task_status(tid, start_at=start_at, end_at=end_at)

            notify_task = notify.tasks.add()
            notify_task.id = tid
            notify_task.value = current_value
            notify_task.status = status

        MessagePipe(self.char_id).put(msg=notify)
