# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       active_value
Date Created:   2015-10-09 17:06
Description:

"""

from dianjing.exception import GameException

from core.mongo import MongoActiveValue
from core.character import Character

from utils.message import MessagePipe

from config import ConfigActiveReward, ConfigErrorMessage, ConfigActiveFunction

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.active_value_pb2 import (
    ACTIVE_VALUE_REWARD_DONE,
    ACTIVE_VALUE_REWARD_ENABLE,
    ACTIVE_VALUE_REWARD_UNABLE,
    ActiveFunctionNotify,
    ActiveValueNotify
)


class ActiveValue(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoActiveValue.exist(self.server_id, self.char_id):
            doc = MongoActiveValue.document()
            doc['_id'] = self.char_id
            MongoActiveValue.db(self.server_id).insert_one(doc)

    @staticmethod
    def cronjob(server_id):
        MongoActiveValue.db(server_id).update_many(
            {},
            {
                '$set': {
                    'rewards': [],
                    'funcs': {}
                }
            }
        )

        for char_id in Character.get_recent_login_char_ids(server_id):
            av = ActiveValue(server_id, char_id)
            av.send_function_notify()
            av.send_value_notify()

    def trig(self, function_name):
        config = ConfigActiveFunction.get(function_name)
        if not config:
            return

        key = 'funcs.{0}'.format(function_name)
        doc = MongoActiveValue.db(self.server_id).find_one(
            {'_id': self.char_id},
            {key: 1}
        )

        current_times = doc['funcs'].get(function_name, 0)
        if current_times >= config.max_times:
            return

        MongoActiveValue.db(self.server_id).update_one(
            {'_id': self.char_id},
            {
                '$inc': {
                    'value': config.value,
                    key: 1
                }
            }
        )

        self.send_function_notify(functions=[function_name])
        self.send_value_notify()

    def get_reward(self, reward_id):
        config = ConfigActiveReward.get(reward_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("ACTIVE_REWARD_NOT_EXIST"))

        doc = MongoActiveValue.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'value': 1, 'rewards': 1}
        )

        if reward_id in doc['rewards']:
            raise GameException(ConfigErrorMessage.get_error_id("ACTIVE_REWARD_ALREADY_GOT"))

        if doc['value'] < config.value:
            raise GameException(ConfigErrorMessage.get_error_id("ACTIVE_REWARD_CAN_NOT_GET"))

        # drop = Drop.generate(config.package)
        # message = "From Active Reward. {0}".format(reward_id)
        # Resource(self.server_id, self.char_id).save_drop(drop, message)
        #
        # MongoActiveValue.db(self.server_id).update_one(
        #     {'_id': self.char_id},
        #     {'$push': {'rewards': reward_id}}
        # )
        #
        # self.send_value_notify()
        # return drop.make_protomsg()

    def send_value_notify(self):
        doc = MongoActiveValue.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'value': 1, 'rewards': 1}
        )

        value = doc['value']

        notify = ActiveValueNotify()
        notify.value = value

        rewards = ConfigActiveReward.INSTANCES.keys()
        for i in rewards:
            notify_reward = notify.rewards.add()
            notify_reward.id = i

            if i in doc['rewards']:
                notify_reward.status = ACTIVE_VALUE_REWARD_DONE
                continue

            config_reward = ConfigActiveReward.get(i)
            if value >= config_reward.value:
                notify_reward.status = ACTIVE_VALUE_REWARD_ENABLE
            else:
                notify_reward.status = ACTIVE_VALUE_REWARD_UNABLE

        MessagePipe(self.char_id).put(msg=notify)

    def send_function_notify(self, functions=None):
        if functions:
            projection = {'funcs.{0}'.format(func): 1 for func in functions}
            act = ACT_UPDATE
        else:
            projection = {'funcs': 1}
            act = ACT_INIT
            functions = ConfigActiveFunction.all_functions()

        doc = MongoActiveValue.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

        notify = ActiveFunctionNotify()
        notify.act = act

        for func in functions:
            notify_function = notify.functions.add()
            notify_function.function_name = func
            notify_function.current_times = doc['funcs'].get(func, 0)

        MessagePipe(self.char_id).put(msg=notify)
