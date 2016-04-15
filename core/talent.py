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

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.


def get_init_talent_doc():
    init_talent = MongoTalent.document_talent()
    for k, v in ConfigTalent.INSTANCES.viewitems():
        if not v['unlock']:
                init_talent[str(v['tp'])] = {str(k): 0}

    return init_talent


class TalentManager(object):
    def __init__(self,server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoTalent.exist(self.server_id, self.char_id):
            self.reset()

    def reset(self):
        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent': 1}
        )

        init_doc = get_init_talent_doc()

        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'talent': init_doc},
            upsert=True,
        )

    def level_up(self, tp, position):
        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent.{0}.{1}'.format(tp, position): 1}
        )

        if not doc['talent'][str(tp)].get(str(position), {}):
            raise GameException(ConfigErrorMessage.get_error_id("TALENT_LOCKED"))

        conf = ConfigTalent.get(doc['talent'][str(tp)][str(position)])
        if not conf.next_id:
            # max level
            raise GameException(ConfigErrorMessage.get_error_id("TALENT_LEVEL_REACH_MAX"))

        using_items = conf.up_need
        resource_classified = ResourceClassification.classify(using_items)
        resource_classified.check_exist(self.server_id, self.char_id)
        resource_classified.remove(self.server_id, self.char_id)

    def unlock(self, tp, position):
        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'talent.{0}.{1}'.format(tp, position): 1}
        )

        if doc['talent'][str(tp)].get(str(position), {}):
            return

        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'talent.{0}.{1}'.format(tp, position): 0},
        )

    def send_notify(self, act=ACT_INIT, tp=None, position=None):
        if tp and position:
            act = ACT_UPDATE
            projection = {'talent.{0}.{1}'.format(tp, position): 1}
        else:
            projection = {'talent': 1}

        doc = MongoTalent.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

