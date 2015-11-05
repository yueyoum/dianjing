# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       sponsor
Date Created:   2015-11-02 10:26
Description:    赞助

"""

import arrow
from django.conf import settings

from dianjing.exception import GameException

from core.mongo import MongoTrainingSponsor
from core.mail import MailManager
from core.package import Drop

from utils.message import MessagePipe

from config import ConfigErrorMessage, ConfigSponsor

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.training_pb2 import (
    TRAINING_SLOT_EMPTY,
    TRAINING_SLOT_NOT_OPEN,
    TRAINING_SLOT_TRAINING,

    TrainingSponsorNotify,
)


class TrainingSponsor(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoTrainingSponsor.exist(self.server_id, self.char_id):
            doc = MongoTrainingSponsor.document()
            doc['_id'] = self.char_id
            MongoTrainingSponsor.db(self.server_id).insert_one(doc)

    def open(self, challenge_id):
        doc = MongoTrainingSponsor.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'sponsors': 1}
        )

        for sponsor_id in ConfigSponsor.INSTANCES.keys():
            if str(sponsor_id) in doc['sponsors']:
                continue

            if ConfigSponsor.get(sponsor_id).condition == challenge_id:
                break
        else:
            return

        MongoTrainingSponsor.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'sponsors.{0}'.format(sponsor_id): 0
            }}
        )

        self.send_notify(sponsor_ids=[sponsor_id])

    def cronjob(self):
        # 每天发送奖励
        # 取消到期合约
        doc = MongoTrainingSponsor.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'sponsors': 1}
        )

        expired = []

        for sponsor_id, start_at_timestamp in doc['sponsors'].iteritems():
            if not start_at_timestamp:
                continue

            remained_days = self.get_remained_days(sponsor_id, start_at_timestamp)
            if remained_days > 0:
                # send mail
                config = ConfigSponsor.get(sponsor_id)

                drop = Drop()
                drop.gold = config.income
                attachment = drop.to_json()

                m = MailManager(self.server_id, self.char_id)
                m.add(config.mail_title, config.mail_content, attachment=attachment)
            else:
                # expired
                expired.append(sponsor_id)

        if expired:
            # 把过期的， start_at_timestamp 设置为0
            updater = {'sponsors.{0}'.format(i): 0 for i in expired}
            MongoTrainingSponsor.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': updater}
            )

        self.send_notify()

    @staticmethod
    def get_remained_days(sponsor_id, start_at_timestamp):
        config = ConfigSponsor.get(sponsor_id)

        now = arrow.utcnow().to(settings.TIME_ZONE)
        start = arrow.get(start_at_timestamp).to(settings.TIME_ZONE)
        passed_days = (now.date() - start.date()).days

        remained_days = config.total_days - passed_days
        if remained_days < 0:
            remained_days = 0

        return remained_days

    def start(self, sponsor_id):
        if not ConfigSponsor.get(sponsor_id):
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_SPONSOR_NOT_EXIST"))

        doc = MongoTrainingSponsor.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'sponsors.{0}'.format(sponsor_id): 1}
        )

        if str(sponsor_id) not in doc['sponsors']:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_SPONSOR_NOT_OPEN"))

        if doc['sponsors'][str(sponsor_id)]:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_SPONSOR_ALREADY_START"))

        MongoTrainingSponsor.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'sponsors.{0}'.format(sponsor_id): arrow.utcnow().timestamp
            }}
        )

        self.send_notify(sponsor_ids=[sponsor_id])

    def send_notify(self, sponsor_ids=None):
        if sponsor_ids:
            act = ACT_UPDATE
            projection = {'sponsors.{0}'.format(i): 1 for i in sponsor_ids}
        else:
            act = ACT_INIT
            projection = {'sponsors': 1}
            sponsor_ids = ConfigSponsor.INSTANCES.keys()

        doc = MongoTrainingSponsor.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

        notify = TrainingSponsorNotify()
        notify.act = act

        for i in sponsor_ids:
            notify_slot = notify.slots.add()
            notify_slot.id = i

            if str(i) not in doc['sponsors']:
                notify_slot.status = TRAINING_SLOT_NOT_OPEN
            else:
                start_at_timestamp = doc['sponsors'][str(i)]
                if start_at_timestamp:
                    notify_slot.status = TRAINING_SLOT_TRAINING
                    notify_slot.remained_days = self.get_remained_days(i, start_at_timestamp)
                else:
                    notify_slot.status = TRAINING_SLOT_EMPTY

        MessagePipe(self.char_id).put(msg=notify)
