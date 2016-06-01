"""
Author:         ouyang
Filename:       talent
Date Created:   2016-04-14 03:36
Description:

"""
from dianjing.exception import GameException

from config import ConfigErrorMessage, ConfigTalent

from core.mongo import MongoTalent
from core.resource import ResourceClassification, money_text_to_item_id
from core.club import Club

from utils.message import MessagePipe

from protomsg.talent_pb2 import TalentNotify

RESET_TALENT_TREE_COST = 100


class TalentManager(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.doc = MongoTalent.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoTalent.document()
            self.doc['_id'] = self.char_id
            self.doc['talents'] = ConfigTalent.INIT_TALENT_IDS
            MongoTalent.db(self.server_id).insert_one(self.doc)

    def remained_points(self):
        p = self.doc['total_point'] - self.doc['cost_point']
        if p < 0:
            p = 0

        return p

    def reset(self):
        if not self.doc['cost_point']:
            raise GameException(ConfigErrorMessage.get_error_id("TALENT_CANNOT_RESET_NOT_USE_POINT"))

        using_items = [(money_text_to_item_id('diamond'), RESET_TALENT_TREE_COST)]
        resource_classified = ResourceClassification.classify(using_items)
        resource_classified.check_exist(self.server_id, self.char_id)
        resource_classified.remove(self.server_id, self.char_id)

        self.doc['talents'] = ConfigTalent.INIT_TALENT_IDS
        self.doc['cost_point'] = 0

        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'talent': self.doc['talents'],
                'cost_point': self.doc['cost_point'],
            }}
        )

        self.send_notify()

        club = Club(self.server_id, self.char_id)
        club.force_load_staffs()
        club.send_notify()

    def add_talent_points(self, amount):
        self.doc['total_point'] += amount
        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'total_point': self.doc['total_point']
            }}
        )

        self.send_notify()

    def level_up(self, talent_id):
        config = ConfigTalent.get(talent_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("TALENT_NOT_EXIST"))

        if not config.next_id:
            raise GameException(ConfigErrorMessage.get_error_id("TALENT_LEVEL_REACH_MAX"))

        if talent_id not in self.doc['talents']:
            raise GameException(ConfigErrorMessage.get_error_id("TALENT_LOCKED"))

        remained_points = self.remained_points()
        if remained_points < config.up_need:
            raise GameException(ConfigErrorMessage.get_error_id("TALENT_POINTS_NOT_ENOUGH"))

        new_talent_id = config.next_id

        self.doc['talents'].remove(talent_id)
        self.doc['talents'].append(new_talent_id)

        unlocked_talents = []
        self.try_unlock(new_talent_id, unlocked_talents)
        self.doc['talents'].extend(unlocked_talents)

        self.doc['cost_point'] += config.up_need

        MongoTalent.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'talents': self.doc['talents'],
                'cost_point': self.doc['cost_point'],
            }}
        )

        self.send_notify()

        club = Club(self.server_id, self.char_id)
        club.force_load_staffs()
        club.send_notify()

    def try_unlock(self, tid, unlocked):
        for i in ConfigTalent.get(tid).trigger_unlock:
            unlocked.append(i)
            self.try_unlock(i, unlocked)

    def get_talent_effect(self):
        effect = []
        for _id in self.doc['talents']:
            eid = ConfigTalent.get(_id).effect_id
            if eid:
                effect.append(eid)

        return effect

    def send_notify(self):
        notify = TalentNotify()
        notify.points = self.remained_points()
        notify.reset_cost = RESET_TALENT_TREE_COST
        notify.talent_id.extend(self.doc['talents'])

        MessagePipe(self.char_id).put(msg=notify)
