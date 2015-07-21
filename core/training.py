# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training
Date Created:   2015-07-21 15:45
Description:

"""

from core.db import get_mongo_db
from core.staff import StaffManger

from utils.message import MessagePipe

from protomsg.training_pb2 import TrainingNotify, TrainingRemoveNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE

class Training(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = get_mongo_db(server_id)

    def buy(self, training_id):
        # TODO cost
        # TODO check training_id exists?

        key = "own_trainings.{0}"
        char = self.mongo.character.find_one(
            {'_id': self.char_id},
            {key: 1}
        )

        amount = char.get('own_trainings', {}).get(str(training_id), 0)
        new_amount = amount + 1

        self.mongo.character.update_one(
            {'_id': self.char_id},
            {'$set': {key: new_amount}}
        )

        self.send_notify(act=ACT_UPDATE, trainings={training_id: new_amount})

    def use(self, staff_id, training_id):
        # TODO check

        key = "own_trainings.{0}".format(training_id)
        char = self.mongo.character.find_one(
            {'_id': self.char_id},
            {key: 1}
        )

        amount = char.get('own_trainings', {}).get(str(training_id), 0)
        if amount <= 0:
            raise RuntimeError("NO AMOUNT!!!")

        sm = StaffManger(self.server_id, self.char_id)
        sm.training_start(staff_id, training_id)

        new_amount = amount - 1
        if new_amount <= 0:
            self.mongo.character.update_one(
                {'_id': self.char_id},
                {'$unset': {key: 1}}
            )

            notify = TrainingRemoveNotify()
            notify.ids.append(training_id)
            MessagePipe(self.char_id).put(msg=notify)
        else:
            self.mongo.character.update_one(
                {'_id': self.char_id},
                {'$set': {key: new_amount}}
            )

            self.send_notify(act=ACT_UPDATE, trainings={training_id: new_amount})


    def send_notify(self, act=ACT_INIT, trainings=None):
        notify = TrainingNotify()
        notify.act = act

        if not trainings:
            char = self.mongo.character.find_one(
                {'_id': self.char_id},
                {'own_trainings': 1}
            )

            trainings = char.get('own_trainings', {})

        for k, v in trainings.iteritems():
            notify_training = notify.trainings.add()
            notify_training.id = int(k)
            notify_training.amount = v


        MessagePipe(self.char_id).put(msg=notify)
