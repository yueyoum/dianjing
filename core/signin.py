# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       signin
Date Created:   2015-09-21 14:52
Description:

"""

import arrow
from django.conf import settings

from dianjing.exception import GameException
from core.mongo import MongoSignIn, MongoCharacter
from core.activity import ActivityCategory
from core.package import Drop
from core.resource import Resource

from utils.message import MessagePipe

from config import ConfigSignIn, ConfigErrorMessage

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.activity_pb2 import ActivitySignInNotify


def get_sign_day(passed_days, sign_days, sign_test_divisor):
    circles = (passed_days - max(sign_days)) / sign_test_divisor
    if circles == 0:
        return passed_days

    index = circles % len(sign_days) - 1
    return sign_days[index]


def is_sign_continued(sign_days, last_day, current_day):
    index = sign_days.index(last_day)
    next_index = index + 1
    if next_index == len(sign_days):
        next_index = 0

    return sign_days[next_index] == current_day


class SignIn(object):
    ACTIVITY_CATEGORY_ID = 1

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.doc = MongoSignIn.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoSignIn.document()
            self.doc['_id'] = self.char_id
            MongoSignIn.db(self.server_id).insert_one(self.doc)

    def next_sign_time(self, sign_id):
        info = self.doc['sign'].get(str(sign_id), {})
        if not info:
            return 0

        last_sign_at = arrow.get(info['last_sign_at']).replace(tzinfo=settings.TIME_ZONE)
        now = arrow.utcnow().to(settings.TIME_ZONE)
        now_date = arrow.Arrow(now.year, now.month, now.day, hour=0, minute=0, second=0, microsecond=0,
                               tzinfo=now.tzinfo)

        if now_date < last_sign_at:
            raise RuntimeError("Sign time error! now_date: {0}, last_sign_at: {1}".format(now_date, last_sign_at))

        if now_date > last_sign_at:
            return 0

        return now_date.replace(days=1).timestamp

    def sign(self, sign_id):
        config = ConfigSignIn.get(sign_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        now = arrow.utcnow().to(settings.TIME_ZONE)

        if now.day % config.valid_test_divisor != config.valid_test_value:
            raise GameException(ConfigErrorMessage.get_error_id("SIGN_CAN_NOT"))

        if self.next_sign_time(sign_id):
            raise GameException(ConfigErrorMessage.get_error_id("SIGN_ALREADY_SIGNED"))

        char_doc = MongoCharacter.db(self.server_id).find_one({'_id': self.char_id}, {'create_at': 1})
        create_at = char_doc['create_at']
        passed_days, seconds = divmod(now.timestamp - create_at, 24 * 3600)
        passed_days += 1

        info = self.doc['sign'].get(str(sign_id), MongoSignIn.document_sign())
        info['last_sign_at'] = now.format("YYYY-MM-DD")

        current_sign_day = get_sign_day(passed_days, config.days, config.valid_test_divisor)
        if info['last_sign_day']:
            info['is_continued'] = is_sign_continued(config.days, info['last_sign_day'], current_sign_day)
        else:
            info['is_continued'] = True

        info['last_sign_day'] = current_sign_day

        MongoSignIn.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'sign.{0}'.format(sign_id): info}},
        )

        self.doc['sign'][str(sign_id)] = info
        self.send_notify(ids=[sign_id])

        package = config.day_reward[current_sign_day]
        drop = Drop.generate(package)
        message = u"From SignIn {0}".format(sign_id)
        Resource(self.server_id, self.char_id).save_drop(drop, message)
        return drop.make_protomsg()


    def send_notify(self, ids=None):
        if not ActivityCategory(self.server_id, self.char_id).is_show(self.ACTIVITY_CATEGORY_ID):
            return

        notify = ActivitySignInNotify()

        if ids:
            act = ACT_UPDATE
        else:
            act = ACT_INIT
            ids = ConfigSignIn.INSTANCES.keys()

        notify.act = act

        now = arrow.utcnow().to(settings.TIME_ZONE)
        char_doc = MongoCharacter.db(self.server_id).find_one({'_id': self.char_id}, {'create_at': 1})
        create_at = char_doc['create_at']
        passed_days, seconds = divmod(now.timestamp - create_at, 24 * 3600)
        if seconds:
            passed_days += 1

        for i in ids:
            config = ConfigSignIn.get(i)
            current_sign_day = get_sign_day(passed_days, config.days, config.valid_test_divisor)
            package = config.day_reward[current_sign_day]

            notify_signin = notify.signins.add()
            notify_signin.id = i
            notify_signin.next_get_time = self.next_sign_time(i)
            notify_signin.drop.MergeFrom(Drop.generate(package).make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)
