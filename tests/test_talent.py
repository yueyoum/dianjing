"""
Author:         ouyang
Filename:       test_talent
Date Created:   2016-04-18 02:50
Description:

"""
import random

from dianjing.exception import GameException

from core.talent import TalentManager, get_init_talent_doc
from core.mongo import MongoTalent

from config import ConfigTalent, ConfigErrorMessage


class TestTalentManager(object):
    def __init__(self):
        self.server_id = 1
        self.char_id = 1

    def setup(self):
        TalentManager(self.server_id, self.char_id)

    def teardown(self):
        MongoTalent.db(self.server_id).delete_one({'_id': self.char_id})

    def test_get_talent_tree(self):
        talent_ids = TalentManager(self.server_id, self.char_id).get_talent_tree()
        init_ids = get_init_talent_doc()
        for k in init_ids:
            assert k in talent_ids

    def test_add_talent_points(self):
        amount = 10000
        TalentManager(self.server_id, self.char_id).add_talent_points(amount)
        doc = MongoTalent.db(self.server_id).find_one({'_id': self.char_id}, {'total': 1})

        assert doc['total'] == amount

    def test_check_talent_points_not_enough(self):
        amount = 10000
        try:
            TalentManager(self.server_id, self.char_id).check_talent_points(amount)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("BAD_MESSAGE")
        else:
            Exception('Error')

    def test_check_talent_points(self):
        self.test_add_talent_points()
        TalentManager(self.server_id, self.char_id).check_talent_points(1000)

    def test_deduct_talent_points(self):
        self.test_add_talent_points()
        TalentManager(self.server_id, self.char_id).deduct_talent_points(1000)

    def test_level_up_lock(self):
        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent': 1}
        )

        _id = 0
        for k in ConfigTalent.INSTANCES.keys():
            if k not in doc['talent']:
                _id = k
                break

        try:
            TalentManager(self.server_id, self.char_id).level_up(_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TALENT_LOCKED")
        else:
            Exception('error')

    def test_level_up_level_max(self):
        self.test_add_talent_points()

        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent': 1}
        )

        _id = random.choice(doc['talent'])
        try:
            for i in range(0, 10):
                TalentManager(self.server_id, self.char_id).level_up(_id)
                conf = ConfigTalent.get(_id)
                if conf.next_id:
                    _id = conf.next_id
                else:
                    break

        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("TALENT_LEVEL_REACH_MAX")
        else:
            Exception("error")

    def test_level_up(self):
        self.test_add_talent_points()

        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent': 1}
        )

        _id = random.choice(doc['talent'])
        conf = ConfigTalent.get(_id)

        TalentManager(self.server_id, self.char_id).level_up(_id)

        doc_af = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent': 1, 'cost': 1}
        )

        assert _id not in doc_af['talent']
        assert conf.next_id in doc_af['talent']
        assert doc_af['cost'] == conf.up_need

    def test_unlock(self):
        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent': 1}
        )

        _id = 0
        keys = ConfigTalent.INSTANCES.keys()
        for k in keys:
            if k not in doc['talent']:
                _id = k
                break

        TalentManager(self.server_id, self.char_id).unlock(_id)

        doc_af = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent': 1}
        )

        assert _id in doc_af['talent']

    def test_get_talent_effect(self):
        assert TalentManager(self.server_id, self.char_id).get_talent_effects()

    def test_send_notify(self):
        TalentManager(self.server_id, self.char_id).send_notify()
