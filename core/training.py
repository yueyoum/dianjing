# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training
Date Created:   2015-07-21 15:45
Description:

"""

from dianjing.exception import GameException

from core.db import MongoDB
from core.mongo import Document
from core.staff import StaffManger
from core.resource import Resource

from utils.message import MessagePipe

from config import ConfigErrorMessage, ConfigTraining

from protomsg.training_pb2 import TrainingNotify, TrainingRemoveNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE


class Training(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = MongoDB.get(server_id)

        doc = self.mongo.staff.find_one({'_id': self.char_id}, {'_id': 1})
        if not doc:
            doc = Document.get("staff")
            doc['_id'] = self.char_id
            self.mongo.staff.insert_one(doc)


    def has_training(self, training_ids):
        if not isinstance(training_ids, (list, tuple)):
            training_ids = [training_ids]

        projection = {"trainings.{0}".format(i): 1 for i in training_ids}
        char = self.mongo.staff.find_one({'_id': self.char_id}, projection)
        for tid in training_ids:
            if str(tid) not in char['trainings']:
                return False

        return True


    def buy(self, training_id):
        config = ConfigTraining.get(training_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_NOT_EXIST"))

        if config.cost_type == 1:
            needs = {'gold': -config.cost_value}
        else:
            needs = {'diamond': -config.cost_value}

        with Resource(self.server_id, self.char_id).check(**needs):
            self.mongo.staff.update_one(
                {'_id': self.char_id},
                {'$inc': {'trainings.{0}'.format(training_id): 1}}
            )


        self.send_notify(act=ACT_UPDATE, ids=[training_id])



    def use(self, staff_id, training_id):
        key = "trainings.{0}".format(training_id)
        doc = self.mongo.staff.find_one(
            {'_id': self.char_id},
            {key: 1}
        )

        amount = doc.get('trainings', {}).get(str(training_id), 0)
        if amount <= 0:
            raise GameException( ConfigErrorMessage.get_error_id("TRAINING_NOT_EXIST") )

        sm = StaffManger(self.server_id, self.char_id)
        if not sm.has_staff(staff_id):
            raise GameException( ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST") )

        sm.training_start(staff_id, training_id)

        new_amount = amount - 1
        if new_amount <= 0:
            self.mongo.staff.update_one(
                {'_id': self.char_id},
                {'$unset': {key: 1}}
            )

            notify = TrainingRemoveNotify()
            notify.ids.append(training_id)
            MessagePipe(self.char_id).put(msg=notify)
        else:
            self.mongo.staff.update_one(
                {'_id': self.char_id},
                {'$set': {key: new_amount}}
            )

            self.send_notify(act=ACT_UPDATE, ids=[training_id])


    def send_notify(self, act=ACT_INIT, ids=None):
        if not ids:
            projection = {'trainings': 1}
        else:
            projection = {'trainings.{0}'.format(i): 1 for i in ids}

        doc = self.mongo.staff.find_one(
            {'_id': self.char_id},
            projection
        )


        notify = TrainingNotify()
        notify.act = act

        for k, v in doc['trainings'].iteritems():
            notify_training = notify.trainings.add()
            notify_training.id = int(k)
            notify_training.amount = v

        MessagePipe(self.char_id).put(msg=notify)
