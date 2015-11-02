# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       sponsor
Date Created:   2015-11-02 10:26
Description:    赞助

"""

import arrow

from dianjing.exception import GameException

from core.mongo import MongoTrainingSponsor

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
        # TODO maybe problem
        # TODO day reward cron job
        doc = MongoTrainingSponsor.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'sponsors': 1}
        )

        updater = {}
        for sponsor_id in ConfigSponsor.INSTANCES.keys():
            if ConfigSponsor.get(sponsor_id).condition != challenge_id:
                continue

            if str(sponsor_id) in doc['sponsors']:
                continue

            updater[str(sponsor_id)] = 0

        if not updater:
            return

        MongoTrainingSponsor.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_notify(sponsor_ids=[int(k) for k in updater.keys()])

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
                    # TODO
                    notify_slot.remained_days = 3
                else:
                    notify_slot.status = TRAINING_SLOT_EMPTY

        MessagePipe(self.char_id).put(msg=notify)
