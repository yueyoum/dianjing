"""
Author:         ouyang
Filename:       talent
Date Created:   2016-04-14 03:36
Description:

"""
from dianjing.exception import GameException

from config import ConfigErrorMessage, ConfigTalent

from core.mongo import MongoTalent
from core.resource import ResourceClassification

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
        doc = MongoTalent.db(self.server_id).find_one({'_id': self.char_id})
        new_items = doc['items']
        for k, v in doc['cost'].iteritems():
            if k in new_items.keys():
                new_items[k] = new_items[k] + doc['cost'][k]
            else:
                new_items[k] = doc['cost'][k]

        init_doc = get_init_talent_doc()
        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'talent': init_doc,
                'cost': {},
                'items': new_items,
            }},
        )

    def check_talent_item(self, items):
        doc = MongoTalent.db(self.server_id).find_one({'_id': self.char_id}, {'items': 1})
        for _id, amount in items:
            if str(_id) not in doc['items'].keys():
                return False

            if doc['items'][str(_id)] < amount:
                return False

        return True

    def deduct_items(self, items):
        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'items': 1}
        )

        new_items = doc['items']
        for _id, amount in items:
            if str(_id) not in new_items.keys():
                return False

            if new_items[str(_id)] < amount:
                return False

            new_items[str(_id)] = new_items[str(_id)] = amount

        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'items': new_items}}
        )

        return True

    def add_talent_items(self, items):
        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'items': 1}
        )

        talent_items = doc['items']
        for _id, amount in items:
            if talent_items.get(str(_id), 0):
                talent_items[str(_id)] += amount
            else:
                talent_items[str(_id)] = amount

        MongoTalent.db(self.server_id).update_one(
            {'_id': self.server_id},
            {'$set': {'items': talent_items}}
        )

    def level_up(self, talent_id):
        doc = MongoTalent.db(self.server_id).find_one({'_id': self.char_id})

        if talent_id not in doc['talent']:
            raise GameException(ConfigErrorMessage.get_error_id("TALENT_LOCKED"))

        conf = ConfigTalent.get(talent_id)
        if not conf.next_id:
            raise GameException(ConfigErrorMessage.get_error_id("TALENT_LEVEL_REACH_MAX"))

        using_items = conf.up_need
        # TODO: item deduct
        # resource_classified = ResourceClassification.classify(using_items)
        # resource_classified.check_exist(self.server_id, self.char_id)
        # resource_classified.remove(self.server_id, self.char_id)

        new_talent = doc['talent']
        new_talent.remove(talent_id)
        new_talent.append(conf.next_id)

        cost = doc['cost']
        for _id, num in using_items:
            if cost.get(str(_id), 0):
                cost[str(_id)] = cost[str(_id)] + num
            else:
                cost[str(_id)] = num

        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'talent': new_talent,
                'cost': cost,
            }}
        )

        if conf.trigger_unlock:
            self.unlock(conf.trigger_unlock)

    def unlock(self, talent_ids):
        if not isinstance(talent_ids, list):
            talent_ids = [talent_ids]

        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent': 1}
        )

        for k in doc['talent']:
            if k not in talent_ids:
                talent_ids.append(k)

        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'talent': talent_ids}},
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
