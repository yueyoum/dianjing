# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       unit
Date Created:   2016-04-08 14:22
Description:

"""

from dianjing.exception import GameException

from core.abstract import AbstractUnit
from core.mongo import MongoUnit
from core.club import Club
from core.resource import ResourceClassification

from utils.message import MessagePipe

from config import ConfigErrorMessage, ConfigUnitUnLock

from protomsg.unit_pb2 import UnitNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE


# 用于NPC的
class NPCUnit(AbstractUnit):
    __slots__ = []

    def __init__(self, _id, step, level):
        super(NPCUnit, self).__init__()
        self.id = _id
        self.step = step
        self.level = level
        self.after_init()


# 用于玩家的
class Unit(AbstractUnit):
    __slots__ = []

    def __init__(self, server_id, char_id, _id, data):
        super(Unit, self).__init__()
        self.server_id = server_id
        self.char_id = char_id
        self.id = _id
        self.step = data['step']
        self.level = data['level']

        self.after_init()

    def level_up(self):
        if self.level >= self.config.max_level:
            raise GameException(ConfigErrorMessage.get_error_id("UNIT_REACH_MAX_LEVEL"))

        using_items = self.config.levels[self.level].update_item_need
        resource_classified = ResourceClassification.classify(using_items)
        resource_classified.check_exist(self.server_id, self.char_id)
        resource_classified.remove(self.server_id, self.char_id)

        self.level += 1

        MongoUnit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {
                'units.{0}.level'.format(self.id): 1
            }}
        )

        self.pre_calculate()
        self.calculate()
        self.send_notify()

    def step_up(self):
        if self.step >= self.config.max_step:
            raise GameException(ConfigErrorMessage.get_error_id("UNIT_REACH_MAX_STEP"))

        if self.level < self.config.steps[self.step].level_limit:
            raise GameException(ConfigErrorMessage.get_error_id("UNIT_LEVEL_NOT_ENOUGH"))

        using_items = self.config.steps[self.step].update_item_need
        resource_classified = ResourceClassification.classify(using_items)
        resource_classified.check_exist(self.server_id, self.char_id)
        resource_classified.remove(self.server_id, self.char_id)

        self.step += 1

        MongoUnit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {
                'units.{0}.step'.format(self.id): 1
            }}
        )

        self.pre_calculate()
        self.calculate()
        self.send_notify()

    def send_notify(self):
        notify = UnitNotify()
        notify.act = ACT_UPDATE
        notify_unit = notify.units.add()
        notify_unit.MergeFrom(self.make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)


def get_init_units():
    units = []
    for k, v in ConfigUnitUnLock.INSTANCES.items():
        if v.need_club_level == 0 and not v.need_unit_level:
            units.append(k)

    return units


class UnitManager(object):
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoUnit.exist(self.server_id, self.char_id):
            doc = MongoUnit.document()
            doc['_id'] = self.char_id

            init_ids = get_init_units()

            for _id in init_ids:
                unit_doc = MongoUnit.document_unit()
                doc['units'][str(_id)] = unit_doc

            MongoUnit.db(self.server_id).insert_one(doc)

    def unlock_club_level_up_listener(self, club_level):
        pass

    def unlock_unit_level_up_listener(self, unit_id, unit_level):
        pass

    def _unlock(self, _id):
        doc = MongoUnit.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'units': 1}
        )

        if str(_id) in doc['units']:
            # already unlocked
            return

        unlock_conf = ConfigUnitUnLock.get(_id)
        club_lv = Club(self.server_id, self.char_id).level
        if club_lv < unlock_conf.need_club_level:
            # TODO error message
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        # TODO: unlock unit lv check
        # for unlock_conf.need_unit_level.

        unit_doc = MongoUnit.document_unit()
        MongoUnit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'units.{0}'.format(_id): unit_doc}},
        )

        self.send_notify(uids=[_id])

    def is_unit_unlocked(self, _id):
        doc = MongoUnit.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'units.{0}'.format(_id): 1}
        )

        return str(_id) in doc['units']

    def check_unit_unlocked(self, _id):
        if not self.is_unit_unlocked(_id):
            raise GameException(ConfigErrorMessage.get_error_id("UNIT_IS_UNLOCKED"))

    def get_unit_object(self, _id):
        # type: (int) -> Unit|None
        doc = MongoUnit.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'units.{0}'.format(_id): 1}
        )

        data = doc['units'].get(str(_id), None)
        if not data:
            return None

        return Unit(self.server_id, self.char_id, _id, data)

    def level_up(self, uid):
        unit = self.get_unit_object(uid)
        if not unit:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        unit.level_up()

    def step_up(self, uid):
        unit = self.get_unit_object(uid)
        if not unit:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        unit.step_up()

    def send_notify(self, uids=None):
        if not uids:
            act = ACT_INIT
            projection = {'units': 1}
        else:
            act = ACT_UPDATE
            projection = {'units.{0}'.format(i): 1 for i in uids}

        doc = MongoUnit.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

        notify = UnitNotify()
        notify.act = act

        for k, v in doc['units'].iteritems():
            notify_unit = notify.units.add()
            unit = Unit(self.server_id, self.char_id, int(k), v)
            notify_unit.MergeFrom(unit.make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)
