# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       activity
Date Created:   2015-09-21 18:03
Description:

"""

import arrow
from django.conf import settings

from dianjing.exception import GameException
from core.mongo import MongoActivity
from core.character import Character
from core.package import Drop
from core.resource import Resource

from utils.message import MessagePipe
from config import ConfigActivityCategory, ConfigSignIn, ConfigLoginReward, ConfigErrorMessage

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.activity_pb2 import ActivityCategoryNotify, ActivityLoginRewardNotify


class ActivityCategory(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.doc = MongoActivity.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoActivity.document()
            self.doc['_id'] = self.char_id
            MongoActivity.db(self.server_id).insert_one(self.doc)

    def is_show(self, category_id):
        config = ConfigActivityCategory.get(category_id)
        if config.fixed:
            # 固定，永远显示
            return True

        return config.end_at < arrow.utcnow()

    def send_notify(self):
        notify = ActivityCategoryNotify()

        for cid in ConfigActivityCategory.INSTANCES.keys():
            if not self.is_show(cid):
                continue

            notify_category = notify.categories.add()
            notify_category.id = cid
            if ConfigActivityCategory.get(cid).end_at:
                notify_category.end_at = ConfigActivityCategory.get(cid).end_at.timestamp

        MessagePipe(self.char_id).put(msg=notify)



class ActivityLoginReward(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id


    def get_reward(self, _id):
        reward_time = self.reward_time(_id)
        if reward_time == -1:
            raise GameException(ConfigErrorMessage.get_error_id("LOGIN_REWARD_ALREADY_GOT"))
        if reward_time > 0:
            raise GameException(ConfigErrorMessage.get_error_id("LOGIN_REWARD_NOT_TO_TIME"))

        MongoActivity.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'done.{0}'.format(_id): 1}}
        )

        drop = Drop.generate(ConfigLoginReward.get(_id).package)
        message = u"LoginReward: {0}".format(_id)
        Resource(self.server_id, self.char_id).save_drop(drop, message)

        self.send_notify(ids=[_id])
        return drop.make_protomsg()


    def reward_time(self, _id):
        config = ConfigLoginReward.get(_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        doc = MongoActivity.db(self.server_id).find_one({'_id': self.char_id})
        if doc and str(_id) in doc['done']:
            return -1

        login_days = Character(self.server_id, self.char_id).login_days
        if login_days >= config.day:
            return 0

        reward_day = arrow.utcnow().to(settings.TIME_ZONE).replace(days=config.day-login_days)
        reward_day = arrow.Arrow(reward_day.year, reward_day.month, reward_day.day, tzinfo=reward_day.tzinfo)
        return reward_day.timestamp


    def send_notify(self, ids=None):
        notify = ActivityLoginRewardNotify()

        if ids:
            act = ACT_UPDATE
        else:
            act = ACT_INIT
            ids = ConfigLoginReward.INSTANCES.keys()

        ids.sort()

        notify.act = act

        for i in ids:
            config = ConfigLoginReward.get(i)
            notify_reward = notify.rewards.add()
            notify_reward.id = i
            notify_reward.reward_time = self.reward_time(i)
            notify_reward.drop.MergeFrom( Drop.generate(config.package).make_protomsg() )

        MessagePipe(self.char_id).put(msg=notify)
