# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training
Date Created:   2015-07-21 15:45
Description:

"""
from dianjing.exception import GameException

from core.mongo import MongoTraining
from core.staff import StaffManger
from core.building import BuildingTrainingCenter
from core.resource import Resource
from core.package import TrainingItem

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

        doc = MongoTraining.db(server_id).find_one({'_id': self.char_id})
        if not doc:
            doc = MongoTraining.document()
            doc['_id'] = self.char_id
            MongoTraining.db(server_id).insert_one(doc)

        if not doc['store']:
            self.refresh(send_notify=False)

    def refresh(self, send_notify=True):
        level = BuildingTrainingCenter(self.server_id, self.char_id).get_level()
        amount = ConfigBuilding.get(BuildingTrainingCenter.BUILDING_ID).get_level(level).value1

        ids = ConfigTraining.refreshed_ids(level, amount)

        trainings = {}
        for i in ids:
            this_id = make_string_id()
            this_doc = MongoTraining.document_training_item()
            this_doc['oid'] = i
            this_doc['item'] = TrainingItem.generate_from_training_id(i).to_json()

            trainings[this_id] = this_doc

        MongoTraining.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'store': trainings}}
        )

        if send_notify:
            self.send_notify()

        return trainings

    def get_training(self, training_id):
        doc = MongoTraining.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'store.{0}'.format(training_id): 1}
        )

        return doc.get('store', {}).get(str(training_id), None)

    def buy(self, training_id):
        training = self.get_training(training_id)
        if not training:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_NOT_EXIST"))

        config = ConfigTraining.get(training['oid'])

        if config.cost_type == 1:
            needs = {'gold': -config.cost_value}
        else:
            needs = {'diamond': -config.cost_value}

        with Resource(self.server_id, self.char_id).check(**needs):
            self.remove(training_id)
            TrainingBag(self.server_id, self.char_id).add(training_id, training['oid'], training['item'])

    def remove(self, training_id):
        MongoTraining.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$unset': {'store.{0}'.format(training_id): 1}}
        )

        notify = TrainingStoreRemoveNotify()
        notify.ids.append(training_id)
        MessagePipe(self.char_id).put(msg=notify)

    def send_notify(self):
        notify = TrainingStoreNotify()
        notify.act = ACT_INIT

        doc = MongoTraining.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'store': 1}
        )

        trainings = doc.get('store', {})
        for k, v in trainings.iteritems():
            notify_training = notify.trainings.add()
            notify_training.id = k
            notify_training.oid = v['oid']

            obj = TrainingItem.loads_from_json(v['item'])
            notify_training.item.MergeFrom(obj.make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)


class TrainingBag(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        doc = MongoTraining.db(server_id).find_one({'_id': self.char_id}, {'_id': 1})
        if not doc:
            doc = MongoTraining.document()
            doc['_id'] = self.char_id
            MongoTraining.db(server_id).insert_one(doc)

    def has_training(self, training_ids):
        if not isinstance(training_ids, (list, tuple)):
            training_ids = [training_ids]

        projection = {"bag.{0}".format(i): 1 for i in training_ids}
        doc = MongoTraining.db(self.server_id).find_one({'_id': self.char_id}, projection)
        for tid in training_ids:
            if tid not in doc['bag']:
                return False

        return True

    def add_from_raw_training(self, oid):
        # 直接从配置中的 训练id 添加
        training_id = make_string_id()
        item = TrainingItem.generate_from_training_id(oid).to_json()
        self.add(training_id, oid, item)


    def add(self, training_id, training_oid, training_item):
        doc = MongoTraining.document_training_item()
        doc['oid'] = training_oid
        doc['item'] = training_item

        MongoTraining.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'bag.{0}'.format(training_id): doc}}
        )

        self.send_notify(ids=[training_id])

    def use(self, staff_id, training_id):
        key = "bag.{0}".format(training_id)
        doc = MongoTraining.db(self.server_id).find_one({'_id': self.char_id}, {key: 1})

        bag = doc.get('bag', {})
        if training_id not in bag:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_NOT_EXIST"))

        sm = StaffManger(self.server_id, self.char_id)
        if not sm.has_staff(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        this_training = bag[training_id]
        sm.training_start(staff_id, this_training['oid'], this_training['item'])

        MongoTraining.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$unset': {key: 1}}
        )

        notify = TrainingRemoveNotify()
        notify.ids.append(training_id)
        MessagePipe(self.char_id).put(msg=notify)

    def send_notify(self, ids=None):
        if not ids:
            projection = {'bag': 1}
            act = ACT_INIT
        else:
            projection = {'bag.{0}'.format(i): 1 for i in ids}
            act = ACT_UPDATE

        doc = MongoTraining.db(self.server_id).find_one({'_id': self.char_id}, projection)
        notify = TrainingNotify()
        notify.act = act

        for k, v in doc['bag'].iteritems():
            notify_training = notify.trainings.add()
            notify_training.id = k
            notify_training.oid = v['oid']

            obj = TrainingItem.loads_from_json(v['item'])
            notify_training.item.MergeFrom(obj.make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)
