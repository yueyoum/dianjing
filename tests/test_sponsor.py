# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       test_sponsor
Date Created:   2015-12-03 16:06
Description:

"""
import arrow

from dianjing.exception import GameException

from core.mongo import MongoTrainingSponsor
from core.training.sponsor import TrainingSponsor

from config import ConfigSponsor, ConfigErrorMessage


one_day_seconds = 24 * 60 * 60


def get_one_available_sponsor(challenge_id):
    for k, v in ConfigSponsor.INSTANCES.iteritems():
        if v.condition <= challenge_id:
            return k


class TestTrainingSponsor(object):
    def setup(self):
        TrainingSponsor(1, 1)

    def teardown(self):
        pass

    def get_one_not_open_sponsor(self):
        doc = MongoTrainingSponsor.db(1).find_one(
            {'_id': 1},
            {'sponsors': 1}
        )

        for i in ConfigSponsor.INSTANCES.keys():
            if str(i) not in doc['sponsors']:
                return i

    def open_sponsor(self):
        sponsor_id = self.get_one_not_open_sponsor()
        TrainingSponsor(1, 1).open(ConfigSponsor.get(sponsor_id).condition)
        return sponsor_id

    def test_open(self):
        sponsor_id = self.get_one_not_open_sponsor()
        TrainingSponsor(1, 1).open(ConfigSponsor.get(sponsor_id).condition)
        doc = MongoTrainingSponsor.db(1).find_one(
            {'_id': 1},
            {'sponsors': 1}
        )

        assert doc['sponsors']

    def test_start_staff_not_exist(self):
        sponsor_id = 0
        for i in range(100000):
            if i not in ConfigSponsor.INSTANCES.keys():
                sponsor_id = i
                break
        try:
            TrainingSponsor(1, 1).start(sponsor_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_SPONSOR_NOT_EXIST")
        else:
            raise Exception("error")

    def test_start_not_open(self):
        sponsor_id = self.get_one_not_open_sponsor()
        try:
            TrainingSponsor(1, 1).start(sponsor_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_SPONSOR_NOT_OPEN")
        else:
            raise Exception("error")

    def test_start_signing(self):
        sponsor_id = self.open_sponsor()
        try:
            TrainingSponsor(1, 1).start(sponsor_id)
            TrainingSponsor(1, 1).start(sponsor_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TRAINING_SPONSOR_ALREADY_START")
        else:
            raise Exception("error")

    def test_start(self):
        sponsor_id = self.open_sponsor()
        TrainingSponsor(1, 1).start(sponsor_id)

        doc = MongoTrainingSponsor.db(1).find_one(
            {'_id': 1},
            {'sponsors': 1}
        )

        assert str(sponsor_id) in doc['sponsors']

    def test_send_notify(self):
        TrainingSponsor(1, 1).send_notify()

    def test_cronjob(self):
        sponsor_id = self.open_sponsor()
        conf = ConfigSponsor.get(sponsor_id)
        for i in range(1, 20):
            MongoTrainingSponsor.db(1).update_one(
                {'_id': i},
                {'$set':
                    {
                        'sponsors.{0}'.format(sponsor_id): arrow.utcnow().timestamp - conf.total_days * one_day_seconds,
                        'has_sponsors': True
                    }},
                upsert=True
            )

        TrainingSponsor(1, 1).cronjob(1)

        for doc in MongoTrainingSponsor.db(1).find():
            assert doc['sponsors'][str(sponsor_id)] == 0
            assert doc['has_sponsors'] == False

