# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training
Date Created:   2015-07-21 15:45
Description:

"""
import random

from dianjing.exception import GameException

from core.db import MongoDB
from core.mongo import Document
from core.staff import StaffManger
from core.building import BuildingTrainingCenter
from core.resource import Resource
from core.package import Package

from utils.message import MessagePipe
from utils.functional import make_string_id

from config import ConfigErrorMessage, ConfigTraining, ConfigBuilding

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.training_pb2 import (
    TrainingNotify,
    TrainingRemoveNotify,
    TrainingStoreNotify,
    TrainingStoreRemoveNotify,
)


class TrainingStore(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = MongoDB.get(server_id)

        doc = self.mongo.training_store.find_one({'_id': self.char_id}, {'trainings': 1})
        if not doc or not doc.get('trainings', {}):
            self.refresh(send_notify=False)


    def refresh(self, send_notify=True):
        level = BuildingTrainingCenter(self.server_id, self.char_id).get_level()
        amount = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).get_level(level).value1

        ids = ConfigTraining.refreshed_ids(level, amount)

        trainings = {}
        for i in ids:
            this_id = make_string_id()
            this_doc = Document.get("training_store.embedded")
            this_doc['oid'] = i

            if ConfigTraining.get(i).tp != 3:
                # 不是技能训练，其他都可能是随机的，这里要生成好
                p = Package.generate(ConfigTraining.get(i).package)
                this_doc['item'] = p.dump_to_item()

            trainings[this_id] = this_doc

        self.mongo.training_store.update_one(
            {'_id': self.char_id},
            {'$set': {'trainings': trainings}},
            upsert=True
        )

        if send_notify:
            self.send_notify()

        return trainings


    def get_training(self, training_id):
        key = 'trainings.{0}'.format(training_id)

        doc = self.mongo.training_store.find_one(
            {'_id': self.char_id},
            {key: 1}
        )

        return doc.get('trainings', {}).get(str(training_id), None)


    def remove(self, training_id):
        key = 'trainings.{0}'.format(training_id)

        self.mongo.training_store.update_one(
            {'_id': self.char_id},
            {'$unset': {key: 1}}
        )

        notify = TrainingStoreRemoveNotify()
        notify.ids.append(training_id)
        MessagePipe(self.char_id).put(msg=notify)



    def send_notify(self):
        notify = TrainingStoreNotify()
        notify.act = ACT_INIT

        doc = MongoDB.get(self.server_id).training_store.find_one(
            {'_id': self.char_id},
            {'trainings': 1}
        )

        trainings = doc.get('trainings', {})
        for k, v in trainings.iteritems():
            notify_training = notify.trainings.add()
            notify_training.id = k
            notify_training.oid = v['oid']
            if v['item']:
                p = Package.load_from_item(v['item'])
                notify_training.item.MergeFrom(p.make_item_protomsg())

        MessagePipe(self.char_id).put(msg=notify)



class TrainingBag(object):
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
        training = TrainingStore(self.server_id, self.char_id).get_training(training_id)
        if not training:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_NOT_EXIST"))

        config = ConfigTraining.get(training['oid'])

        if config.cost_type == 1:
            needs = {'gold': -config.cost_value}
        else:
            needs = {'diamond': -config.cost_value}

        with Resource(self.server_id, self.char_id).check(**needs):
            TrainingStore(self.server_id, self.char_id).remove(training_id)
            self.add(training_id, training)


    def add(self, training_id, training_data):
        self.mongo.staff.update_one(
            {'_id': self.char_id},
            {'$set': {'trainings.{0}'.format(training_id): training_data}}
        )

        self.send_notify(act=ACT_UPDATE, ids=[training_id])


    def use(self, staff_id, training_id):
        key = "trainings.{0}".format(training_id)
        doc = self.mongo.staff.find_one(
            {'_id': self.char_id},
            {key: 1}
        )

        trainings = doc.get('trainings', {})
        if training_id not in trainings:
            raise GameException( ConfigErrorMessage.get_error_id("TRAINING_NOT_EXIST") )

        sm = StaffManger(self.server_id, self.char_id)
        if not sm.has_staff(staff_id):
            raise GameException( ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST") )

        this_training = trainings[training_id]
        sm.training_start(staff_id, this_training)

        self.mongo.staff.update_one(
            {'_id': self.char_id},
            {'$unset': {key: 1}}
        )

        notify = TrainingRemoveNotify()
        notify.ids.append(training_id)
        MessagePipe(self.char_id).put(msg=notify)



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
            notify_training.id = k
            notify_training.oid = v['oid']
            if v['item']:
                p = Package.load_from_item(v['item'])
                notify_training.item.MergeFrom(p.make_item_protomsg())

        MessagePipe(self.char_id).put(msg=notify)
