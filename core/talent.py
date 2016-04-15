"""
Author:         ouyang
Filename:       talent
Date Created:   2016-04-14 03:36
Description:

"""
from dianjing.exception import GameException

from config import ConfigErrorMessage, ConfigTalent

from core.mongo import MongoTalent
# from core.resource import ResourceClassification

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
            MongoTalent.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'talent': init_doc
                    }
                },
                upsert=True,
            )

    def reset(self):
        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'points': 1, 'cost': 1}
        )

        init_doc = get_init_talent_doc()
        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'talent': init_doc,
                'points': doc['points'] + doc['cost'],
                'cost': 0}},
            upsert=True,
        )

    def add_points(self, num):
        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {'points': num}}
        )

    def level_up(self, talent_id):
        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent': 1, 'points': 1}
        )

        if talent_id not in doc['talent']:
            raise GameException(ConfigErrorMessage.get_error_id("TALENT_LOCKED"))

        conf = ConfigTalent.get(talent_id)
        if not conf.next_id:
            raise GameException(ConfigErrorMessage.get_error_id("TALENT_LEVEL_REACH_MAX"))

        if conf.up_need > doc['points']:
            raise GameException(ConfigErrorMessage.get_error_id("TALENT_POINTS_NOT_ENOUGH"))

        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'talent': conf.next_id,
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

    def send_notify(self, tp=None, position=None):
        if tp and position:
            projection = {'points': 1, 'talent.{0}.{1}'.format(tp, position): 1}
        else:
            projection = {'points': 1, 'talent': 1}

        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

        notify = TalentNotify()
        notify.points = doc['points']
        notify.reset_cost = 0

        for d in doc['talent']:
            talent_id = notify.talent_id.add()
            talent_id.MergeFrom(d)

        MessagePipe(self.char_id).put(msg=notify)


