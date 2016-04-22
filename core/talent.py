"""
Author:         ouyang
Filename:       talent
Date Created:   2016-04-14 03:36
Description:

"""
from dianjing.exception import GameException

from config import ConfigErrorMessage, ConfigTalent

from core.mongo import MongoTalent
from core.resource import ResourceClassification, TALENT_ITEM_ID

from utils.message import MessagePipe

from protomsg.talent_pb2 import TalentNotify


RESET_TALENT_TREE_COST = 100


def get_init_talent_doc():
    init_talent = []
    for k, v in ConfigTalent.INSTANCES.viewitems():
        if not v.unlock:
                init_talent.append(k)

    return init_talent


class TalentManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoTalent.exist(self.server_id, self.char_id):
            init_doc = get_init_talent_doc()
            doc = MongoTalent.document()
            doc['_id'] = self.char_id
            doc['talent'] = init_doc

            MongoTalent.db(self.server_id).insert_one(doc)

    def get_talent_tree(self):
        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent': 1}
        )

        return doc['talent']

    def reset(self):
        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'cost': 1}
        )
        if doc['cost'] == 0:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        using_items = [(30000, RESET_TALENT_TREE_COST)]
        resource_classified = ResourceClassification.classify(using_items)
        resource_classified.check_exist(self.server_id, self.char_id)
        resource_classified.remove(self.server_id, self.char_id)

        init_doc = get_init_talent_doc()
        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'talent': init_doc,
                'cost': 0,
            }},
        )

        self.send_notify()

    def check_talent_points(self, amount):
        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'total': 1, 'cost': 1}
        )

        if doc['total'] - doc['cost'] < amount:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

    def deduct_talent_points(self, amount):
        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {'cost': amount}}
        )

        self.send_notify()

    def add_talent_points(self, amount):
        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {'total': amount}}
        )
        self.send_notify()

    def level_up(self, talent_id):
        doc = MongoTalent.db(self.server_id).find_one({'_id': self.char_id})

        if talent_id not in doc['talent']:
            raise GameException(ConfigErrorMessage.get_error_id("TALENT_LOCKED"))

        conf = ConfigTalent.get(talent_id)
        if not conf.next_id:
            raise GameException(ConfigErrorMessage.get_error_id("TALENT_LEVEL_REACH_MAX"))

        using_items = [(TALENT_ITEM_ID, conf.up_need)]
        resource_classified = ResourceClassification.classify(using_items)
        resource_classified.check_exist(self.server_id, self.char_id)
        resource_classified.remove(self.server_id, self.char_id)

        new_talent = doc['talent']
        new_talent.remove(talent_id)
        new_talent.append(conf.next_id)

        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'talent': new_talent,
                'cost': doc['cost'] + conf.up_need,
            }}
        )

        if conf.trigger_unlock:
            self.unlock(conf.trigger_unlock)

        self.send_notify()

    def unlock(self, talent_ids):
        if not isinstance(talent_ids, list):
            talent_ids = [talent_ids]

        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent': 1}
        )

        new_talents = doc['talent']
        for k in talent_ids:
            if k not in doc['talent']:
                new_talents.append(k)

        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'talent': new_talents}},
        )

    def get_talent_effect(self):
        talent_tree = self.get_talent_tree()
        effect = []
        for _id in talent_tree:
            effect.append(ConfigTalent.get(_id).effect_id)

        return effect

    def send_notify(self):
        doc = MongoTalent.db(self.server_id).find_one({'_id': self.char_id})

        notify = TalentNotify()
        notify.points = doc['total'] - doc['cost']
        notify.reset_cost = RESET_TALENT_TREE_COST

        for d in doc['talent']:
            notify.talent_id.append(d)
        MessagePipe(self.char_id).put(msg=notify)
