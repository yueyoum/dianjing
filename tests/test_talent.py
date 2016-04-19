"""
Author:         ouyang
Filename:       test_talent
Date Created:   2016-04-18 02:50
Description:

"""
import random

from dianjing.exception import GameException

from core.talent import TalentManager
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
        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent': 1}
        )

        _id = random.choice(doc['talent'])
        try:
            for i in range(1, 10):
                TalentManager(self.server_id, self.char_id).level_up(_id)
                conf = ConfigTalent.get(_id)
                if conf.next_id:
                    _id = conf.next_id

        except GameException as e:
            print e.error_id
            assert e.error_id == ConfigErrorMessage.get_error_id("TALENT_LEVEL_REACH_MAX")
        else:
            Exception("error")

    def test_level_up(self):
        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent': 1}
        )

        _id = random.choice(doc['talent'])
        conf = ConfigTalent.get(_id)
        # TODO: add cost item
        # need_item = {}
        # for item_id, amount in conf.up_need:
        #     need_item['amount'] = amount
        #     Bag(self.server_id, self.char_id).add(item_id, **need_item)

        TalentManager(self.server_id, self.char_id).level_up(_id)

        doc_af = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent': 1, 'cost': 1}
        )

        assert _id not in doc_af['talent']
        assert conf.next_id in doc_af['talent']

        for item_id, amount in conf.up_need:
            assert doc_af['cost'].get(str(item_id), 0) == amount

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

    def test_get_talent(self):
        assert TalentManager(self.server_id, self.char_id).get_talent()

    def test_send_notify(self):
        TalentManager(self.server_id, self.char_id).send_notify()
