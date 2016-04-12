# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       signin
Date Created:   2015-10-13 11:33
Description:

"""

import arrow
from django.conf import settings

from dianjing.exception import GameException
from core.mongo import MongoSignIn
from core.resource import Resource
from core.mail import MailManager

from utils.message import MessagePipe

from config import ConfigSignIn, ConfigErrorMessage

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.activity_pb2 import ActivitySignInNotify


class SignStatus(object):
    NOW = 1
    NEXT_TIME = 2

    def __init__(self, sign_id):
        self.sign_id = sign_id
        self.tp = 0  # NOW | NEXT_TIME, 当前是否可以签到
        self.date = arrow.utcnow()  # 签到的时间
        self.sign_day = 0  # 签到日，对应配置中的day_reward中的天数
        self.is_big_reward = False  # 是否拿大奖
        self.is_circle_start = False  # 是否是新的循环开始

    @property
    def sign_timestamp(self):
        if self.tp == SignStatus.NOW:
            return 0
        return self.date.timestamp

    @property
    def package_id(self):
        return ConfigSignIn.get(self.sign_id).get_package_id(self.sign_day)


class SignBaseActivity(object):
    ACTIVITY_ID = 0

    def __init__(self):
        self.id = self.ACTIVITY_ID
        self.now = arrow.utcnow().to(settings.TIME_ZONE)

        self.sign_date = self.get_now_sign_date()
        self.next_sign_date = self.get_next_sign_date()

    def get_now_sign_date(self):
        """

        :rtype : arrow.Arrow | None
        """
        return arrow.get(self.now.date()).replace(tzinfo=self.now.tzinfo)

    def get_next_sign_date(self):
        """

        :rtype : arrow.Arrow
        """
        next_day = self.now.replace(days=1)
        return arrow.get(next_day.date()).replace(tzinfo=self.now.tzinfo)

    def get_sign_status(self, sign_date_sequence):
        """

        :rtype : SignStatus
        """
        ss = SignStatus(self.id)
        ss.tp = SignStatus.NOW
        ss.date = self.sign_date
        ss.sign_day = self.get_sign_day()
        ss.is_big_reward = self.is_big_reward(sign_date_sequence)
        ss.is_circle_start = self.is_circle_start(sign_date_sequence)

        if not sign_date_sequence:
            if ss.date:
                return ss

            ss.tp = SignStatus.NEXT_TIME
            ss.date = self.next_sign_date
            return ss

        last_sign_date = sign_date_sequence[-1]
        last_sign_date = arrow.get(last_sign_date, 'YYYY-MM-DD HH:mm:ss').to(settings.TIME_ZONE)
        if last_sign_date.date() < self.now.date():
            if ss.date:
                return ss

                # ss.tp = SignStatus.NEXT_TIME
                # ss.date = self.next_sign_date
                # return ss

        ss.tp = SignStatus.NEXT_TIME
        ss.date = self.next_sign_date
        return ss

    def get_sign_day(self):
        if self.sign_date:
            return self.sign_date.day
        return self.next_sign_date.day

    def is_big_reward(self, sign_date_sequence):
        return False

    def is_circle_start(self, sign_date_sequence):
        sign_day = self.get_sign_day()
        config = ConfigSignIn.get(self.id)
        return config.days.index(sign_day) == 0


class SignActivity1(SignBaseActivity):
    ACTIVITY_ID = 1

    def get_sign_day(self):
        return self.now.isoweekday()

    def is_big_reward(self, sign_date_sequence):
        weekday = self.now.isoweekday()
        if weekday != 7:
            return False

        if len(sign_date_sequence) != 6:
            return False

        for i in range(1, 7):
            date = arrow.get(sign_date_sequence[6 - i], 'YYYY-MM-DD HH:mm:ss').to(settings.TIME_ZONE)
            if self.now.replace(days=-i).date() != date.date():
                return False

        return True


class SignActivity2(SignBaseActivity):
    ACTIVITY_ID = 2

    def is_big_reward(self, sign_date_sequence):
        return len(sign_date_sequence) == 29

    def is_circle_start(self, sign_date_sequence):
        return len(sign_date_sequence) == 30


class SignActivity3(SignBaseActivity):
    ACTIVITY_ID = 3

    def get_sign_day(self):
        return self.now.isoweekday()


class SignActivity4(SignBaseActivity):
    ACTIVITY_ID = 4

    def get_now_sign_date(self):
        if self.now.day % 2 == 1:
            return super(SignActivity4, self).get_now_sign_date()

        return None

    def get_next_sign_date(self):
        next_day = self.now.replace(days=1)

        while True:
            if next_day.day % 2 == 1:
                return arrow.get(next_day.date()).replace(tzinfo=self.now.tzinfo)

            next_day = next_day.replace(days=1)


class SignActivity5(SignBaseActivity):
    ACTIVITY_ID = 5

    def get_now_sign_date(self):
        if self.now.day % 2 == 0:
            return super(SignActivity5, self).get_now_sign_date()

        return None

    def get_next_sign_date(self):
        next_day = self.now.replace(days=1)

        while True:
            if next_day.day % 2 == 0:
                return arrow.get(next_day.date()).replace(tzinfo=self.now.tzinfo)

            next_day = next_day.replace(days=1)


class SignEntry(object):
    SIGN_ACTIVITY_MAP = {
        1: SignActivity1,
        2: SignActivity2,
        3: SignActivity3,
        4: SignActivity4,
        5: SignActivity5,
    }

    def __new__(cls, activity_id):
        """

        :rtype : SignBaseActivity
        """
        return cls.SIGN_ACTIVITY_MAP[activity_id]()


class SignIn(object):
    ACTIVITY_CATEGORY_ID = 1

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoSignIn.exist(self.server_id, self.char_id):
            doc = MongoSignIn.document()
            doc['_id'] = self.char_id
            MongoSignIn.db(self.server_id).insert_one(doc)

    def sign(self, sign_id):
        config = ConfigSignIn.get(sign_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if not config.display:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        doc = MongoSignIn.db(self.server_id).find_one({'_id': self.char_id})
        sign_sequence = doc['sign'].get(str(sign_id), [])
        se = SignEntry(sign_id)
        ss = se.get_sign_status(sign_sequence)

        if ss.tp == SignStatus.NEXT_TIME:
            raise GameException(ConfigErrorMessage.get_error_id("SIGN_ALREADY_SIGNED"))

        package_id = ss.package_id
        sign_day = ss.sign_day

        if ss.is_circle_start:
            MongoSignIn.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'sign.{0}'.format(sign_id): [se.now.to('UTC').format("YYYY-MM-DD HH:mm:ss")]
                }}
            )
        else:
            MongoSignIn.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$push': {
                    'sign.{0}'.format(sign_id): se.now.to('UTC').format("YYYY-MM-DD HH:mm:ss")
                }}
            )

        # if ss.is_big_reward:
        #     big_reward = Drop.generate(config.circle_package).to_json()
        #     mail = MailManager(self.server_id, self.char_id)
        #     mail.add(
        #         title=config.mail_title,
        #         content=config.mail_content,
        #         attachment=big_reward
        #     )
        #
        # drop = Drop.generate(package_id)
        # message = u"From SignIn {0}, Day {1}".format(sign_id, sign_day)
        # Resource(self.server_id, self.char_id).save_drop(drop, message)
        #
        # self.send_notify(ids=[sign_id])
        # return drop.make_protomsg()

    def send_notify(self, ids=None):
        from core.activity import ActivityCategory

        if not ActivityCategory(self.server_id, self.char_id).is_show(self.ACTIVITY_CATEGORY_ID):
            return

        notify = ActivitySignInNotify()

        if ids:
            act = ACT_UPDATE
        else:
            act = ACT_INIT
            ids = ConfigSignIn.INSTANCES.keys()

        notify.act = act
        doc = MongoSignIn.db(self.server_id).find_one({'_id': self.char_id})

        # for i in ids:
        #     if not ConfigSignIn.get(i).display:
        #         continue
        #
        #     sign_sequence = doc['sign'].get(str(i), [])
        #     se = SignEntry(i)
        #     ss = se.get_sign_status(sign_sequence)
        #
        #     notify_signin = notify.signins.add()
        #     notify_signin.id = i
        #     notify_signin.next_get_time = ss.sign_timestamp
        #     notify_signin.drop.MergeFrom(Drop.generate(ss.package_id).make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)
