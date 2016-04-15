"""
Author:         ouyang
Filename:       talent
Date Created:   2016-04-14 03:36
Description:

"""
from dianjing.exception import GameException

from config import ConfigErrorMessage, ConfigTalent

from core.mongo import MongoTalent

from utils.message import MessagePipe

from protomsg.talent_pb2 import TalentNotify


def get_init_talent_doc():
    init_talent = []
    for k, v in ConfigTalent.INSTANCES.viewitems():
        if not v['unlock']:
                init_talent.append(k)

    return init_talent


class TalentManager(object):
    def __init__(self,server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoTalent.exist(self.server_id, self.char_id):
            init_doc = get_init_talent_doc()
            doc = MongoTalent.document()
            doc['_id'] = self.char_id
            doc['talent'] = init_doc

            MongoTalent.db(self.server_id).insert_one(doc)

    def reset(self):
        init_doc = get_init_talent_doc()
        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'talent': init_doc,
                'cost': 0,
            }},
        )

    def add_points(self, num):
        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {'total': num}}
        )

    def level_up(self, talent_id):
        doc = MongoTalent.db(self.server_id).find_one({'_id': self.char_id})

        if talent_id not in doc['talent']:
            raise GameException(ConfigErrorMessage.get_error_id("TALENT_LOCKED"))

        conf = ConfigTalent.get(talent_id)
        if not conf.next_id:
            raise GameException(ConfigErrorMessage.get_error_id("TALENT_LEVEL_REACH_MAX"))

        if conf.up_need > (doc['total'] - doc['cost']):
            raise GameException(ConfigErrorMessage.get_error_id("TALENT_POINTS_NOT_ENOUGH"))

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

    def unlock(self, talent_id):
        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent': 1}
        )

        if talent_id in doc['talent']:
            return

        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$push': {'talent': talent_id}},
        )

    def get_talent(self):
        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent': 1}
        )

        return doc['talent']

    def send_notify(self):
        doc = MongoTalent.db(self.server_id).find_one({'_id': self.char_id})

        notify = TalentNotify()
        notify.points = doc['total'] - doc['cost']
        notify.reset_cost = 0

        for d in doc['talent']:
            talent_id = notify.talent_id.add()
            talent_id.MergeFrom(d)

        MessagePipe(self.char_id).put(msg=notify)


