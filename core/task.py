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
    """
    获取 任务目标当前进度
        如果是累加比较( mode == 1 ), 直接从配置文件中返回数值
        如果是直接比较, 转到比较源获取进度值
    """
    config = ConfigTaskTargetType.get(target_id)
    if config.mode == 1:
        key = '{0}:{1}'.format(target_id, param)
        return task_data.get(key, 0)

    module, class_name, func_name = config.compare_source.rsplit('.', 2)
    module = __import__(module, fromlist=[class_name], level=0)
    cls = getattr(module, class_name)
    obj = cls(server_id, char_id)

    func = getattr(obj, func_name)
    if config.has_param:
        return func(param)
    else:
        return func()


class TaskManager(object):
    """
    任务管理系统
        管理任务各个功能
    """
    def __init__(self, server_id, char_id):
        """
        初始化 TaskManager 数据
            如果 玩家 在 MongoTask 没有数据,
            从 任务头 ConfigTask.HEAD_TASKS 获取任务,
            如果不是 支线任务 , 添加到 MongoTask
            检测任务是否完成 (防止任务添加时任务已完成导致玩家任务不能继续进行)
        """
        self.server_id = server_id
        self.char_id = char_id

        if not MongoTask.exist(self.server_id, self.char_id):
            doc = MongoTask.document()
            doc['_id'] = self.char_id

            # 初始化主线 和 日常
            doing = {}
            for tid in ConfigTask.HEAD_TASKS:
                config = ConfigTask.get(tid)
                if not config.is_branch_task():
                    doing[str(tid)] = {}

            doc['doing'] = doing
            MongoTask.db(self.server_id).insert_one(doc)

        self.check(send_notify=False)

    @classmethod
    def cronjob(cls, server_id):
        """
        定时刷新任务接口
            更新最近登录用户任务
        """
        char_ids = Character.get_recent_login_char_ids(server_id)
        for cid in char_ids:
            cls(server_id, cid).refresh()

    def refresh(self):
        """
        日常任务刷新
            1, 取出玩家任务日志
            2, 去除日常任务
                2.1, 组装 doing 日常任务去除语句
                2.2, 组装 finish 日常任务去除语句
                2.3, 去除数据
            3, 更新日常任务
                3.1, 从TaskConfig获取日常任务链链首任务
                3.2, 加入玩家任务数据库
        """
        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'history': 0})

        doing_ids = doc['doing'].keys()
        finish_ids = doc['finish']

        daily_doing_updater = {}
        for i in doing_ids:
            if ConfigTask.get(int(i)).is_daily_task():
                daily_doing_updater['doing.{0}'.format(i)] = 1

        daily_finish_updater = []
        for i in finish_ids:
            if ConfigTask.get(i).is_daily_task():
                daily_finish_updater.append(i)

        # remove old
        updater = {}
        if daily_doing_updater:
            updater['$unset'] = daily_doing_updater

        if daily_finish_updater:
            updater['$pullAll'] = {'finish': daily_finish_updater}

        if updater:
            MongoTask.db(self.server_id).update_one(
                {'_id': self.char_id},
                updater
            )

        # set new
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
        """
        添加任务
            1, 检测任务是否可添加
                1.1, 任务是否存在
                1.2, 任务是否已接受
                1.3, 任务是否可重复完成
            2, 写入数据库
            3, 检测是否已完成
        """
        config = ConfigTask.get(task_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id('TASK_NOT_EXIST'))

        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id})
        if str(task_id) in doc['doing']:
            raise GameException(ConfigErrorMessage.get_error_id('TASK_ALREADY_DOING'))

        if task_id in doc['finish'] or task_id in doc['history']:
            raise GameException(ConfigErrorMessage.get_error_id('TASK_CAN_NOT_REPRODUCE'))

        MongoTask.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'doing.{0}'.format(task_id): {}}}
        )

        self.check(task_ids=[task_id])

    def get_reward(self, task_id):
        """
        领取任务奖励
            1 获取 任务 configure, 检测任务是否存在，并以完成
            2 发送奖励
            3 检查是否是日常任务, 如果不是日常任务: 从 finish 中移除, 并 写入 history
            4 通知客户端移除任务
            5 如果有 next_id, 添加
            6 返回结果

        """
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

        self.send_remove_notify(task_id)
        if config.next_task:
            self.add_task(config.next_task)

        return drop.make_protomsg()

    def trigger(self, trigger, num):
        """
        任务触发
            1 通过触发类型获取可触发任务列表
            2 获取玩家任务数据
            3 判断触发任务是否可添加
                任务在 history (不能重复完成) , doing (正在进行中), finish (已完成) 中,
                或触发值低于可触发值的, 不可添加)
        """
        task_ids = ConfigTask.filter(trigger=trigger).keys()
        doc = MongoTask.db(self.server_id).find_one({'_id': self.char_id})

        doing_ids = [int(i) for i in doc['doing'].keys()]
        doc_task_ids = set(doc['history']) | set(doc['finish']) | set(doing_ids)

        for task_id in task_ids:
            config = ConfigTask.get(task_id)

            # TODO, 更完备的判断
            if config.trigger_value <= num and config.id not in doc_task_ids:
                self.add_task(task_id)

    def update(self, target_id, param, value):
        """
        更新任务数据
            1 获取与目标相关的任务 task_ids, 如果为空, 直接返回
            2 获取 doing 任务信息
            3 获取 目标 类型配置
            4 如果是累加比较类型, 更新任务数据 (非累加类型不用处理, 会在check中检测)
            5 检查任务是否完成
        """
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

        self.check(task_ids=task_ids)

    def check(self, task_ids=None, send_notify=True):
        """
        检查任务是否完成
            1 从任务数据库中取出正在进行的任务 doing ;
                如果 task_ids == None, task_ids 为数据库 doing 任务id

            2 遍历检测是否完成
                2.1 获取任务 config
                2.2 从 get_target_current_value 获取任务当前进度
                2.3 如果任务 compare_type == 1, 比较方式为 >=; 否则, 为<=
                2.4 如果任务完成, 把任务从 doing 中清除( 写入 unsetter 语句中),
                    并把任务加到 finish 中( 写入 finish_ids)

            3 更新到玩家数据库

            4 同步任务信息到客户端

        """
        docs = MongoTask.db(self.server_id).find_one({'_id': self.char_id}, {'doing': 1})
        if not task_ids:
            task_ids = [int(i) for i in docs['doing']]

        unsetter = {}
        finish_ids = []

        for tid in task_ids:
            task_data = docs['doing'].get(str(tid), None)
            if task_data is None:
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

        if send_notify:
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
        """
        任务移除
            通知客户端移除任务
        """
        notify = TaskRemoveNotify()
        notify.id = _id
        MessagePipe(self.char_id).put(msg=notify)

    def send_notify(self, ids=None):
        """
        任务通知
            通知玩家任务详情

            ACT_INIT    客户端会清除数据, 然后重新赋值
            ACT_UPDATE  客户端更新对应数据
        """
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

            for target_key, _ in ConfigTask.get(int(k)).targets.iteritems():
                target_id, param = target_key
                notify_task_target = notify_task.targets.add()
                notify_task_target.id = target_id
                notify_task_target.param = param
                notify_task_target.current_value = get_target_current_value(self.server_id, self.char_id, target_id,
                                                                            param, v)

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
