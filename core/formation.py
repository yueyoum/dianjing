# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       formation
Date Created:   2016-04-12 14-56
Description:

"""

import random

from dianjing.exception import GameException

from core.mongo import MongoFormation
from core.staff import StaffManger
from core.unit import UnitManager
from core.club import Club

from utils.message import MessagePipe

from config import ConfigErrorMessage

from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT
from protomsg.formation_pb2 import (
    FORMATION_SLOT_EMPTY,
    FORMATION_SLOT_NOT_OPEN,
    FORMATION_SLOT_USE,
    FormationNotify,
)

MAX_SLOT_AMOUNT = 6


class Formation(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.doc = MongoFormation.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoFormation.document()
            self.doc['_id'] = self.char_id
            self.doc['position'] = [0] * 30
            MongoFormation.db(self.server_id).insert_one(self.doc)

    def is_staff_in_formation(self, staff_id):
        for _, v in self.doc['slots'].iteritems():
            if v['staff_id'] and v['staff_id'] == staff_id:
                return True

        return False

    def in_formation_staffs(self):
        # type: () -> dict[str, dict[str, int]]
        staffs = {}
        for slot_id, v in self.doc['slots'].iteritems():
            if v['staff_id']:
                position = self.doc['position'].index(int(slot_id))
                staffs[v['staff_id']] = {
                    'unit_id': v['unit_id'],
                    'position': position
                }

        return staffs

    def open_slot(self, staff_unique_id="", unit_id=0, send_notify=True):
        if staff_unique_id:
            # TODO error code
            StaffManger(self.server_id, self.char_id).check_staff(ids=[staff_unique_id])

            if staff_unique_id in self.in_formation_staffs():
                raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        slot_id = len(self.doc['slots']) + 1
        if slot_id > MAX_SLOT_AMOUNT:
            # TODO error code
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        data = MongoFormation.document_slot()
        data['staff_id'] = staff_unique_id
        data['unit_id'] = unit_id

        empty_positions = [_index for _index, _slot_id in enumerate(self.doc['position']) if _slot_id == 0]
        pos = random.choice(empty_positions)

        self.doc['slots'][str(slot_id)] = data
        self.doc['position'][pos] = slot_id

        MongoFormation.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'slots.{0}'.format(slot_id): data,
                'position.{0}'.format(pos): slot_id
            }}
        )

        if send_notify:
            self.send_notify(slot_ids=[slot_id])

        return slot_id

    def set_staff(self, slot_id, staff_id):
        if str(slot_id) not in self.doc['slots']:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_SLOT_NOT_OPEN"))

        StaffManger(self.server_id, self.char_id).check_staff(ids=[staff_id])

        if staff_id in self.in_formation_staffs():
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_STAFF_ALREADY_IN"))

        old_staff_id = self.doc['slots'][str(slot_id)]['staff_id']

        self.doc['slots'][str(slot_id)]['staff_id'] = staff_id
        self.doc['slots'][str(slot_id)]['unit_id'] = 0

        MongoFormation.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'slots.{0}.staff_id'.format(slot_id): staff_id,
                'slots.{0}.unit_id'.format(slot_id): 0,
            }}
        )

        self.send_notify(slot_ids=[slot_id])

        # NOTE 阵型改变，重新load staffs
        changed_staff_ids = self.in_formation_staffs().keys()
        if old_staff_id:
            changed_staff_ids.append(old_staff_id)

        club = Club(self.server_id, self.char_id)
        club.force_load_staffs()
        club.send_notify()
        StaffManger(self.server_id, self.char_id).send_notify(ids=changed_staff_ids)

    def set_unit(self, slot_id, unit_id):
        if str(slot_id) not in self.doc['slots']:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_SLOT_NOT_OPEN"))

        UnitManager(self.server_id, self.char_id).check_unit_unlocked(unit_id)

        staff_id = self.doc['slots'][str(slot_id)]['staff_id']
        if not staff_id:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_SLOT_NO_STAFF"))

        self.doc['slots'][str(slot_id)]['unit_id'] = unit_id

        MongoFormation.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'slots.{0}.unit_id'.format(slot_id): unit_id
            }}
        )

        self.send_notify(slot_ids=[slot_id])

        u = UnitManager(self.server_id, self.char_id).get_unit_object(unit_id)
        s = StaffManger(self.server_id, self.char_id).get_staff_object(staff_id)
        s.set_unit(u)
        s.calculate()
        s.make_cache()

        Club(self.server_id, self.char_id).send_notify()

    def move_slot(self, slot_id, to_index):
        if str(slot_id) not in self.doc['slots']:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_SLOT_NOT_OPEN"))

        if to_index < 0 or to_index > 30:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        this_slot_index = self.doc['position'].index(slot_id)
        target_index_slot_id = self.doc['position'][to_index]

        self.doc['position'][to_index] = slot_id
        self.doc['position'][this_slot_index] = target_index_slot_id

        MongoFormation.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'position.{0}'.format(to_index): slot_id,
                'position.{0}'.format(this_slot_index): target_index_slot_id
            }}
        )

        self.send_notify(slot_ids=[slot_id, target_index_slot_id])

    def send_notify(self, slot_ids=None):
        if slot_ids:
            act = ACT_UPDATE
        else:
            act = ACT_INIT
            slot_ids = range(1, MAX_SLOT_AMOUNT + 1)

        notify = FormationNotify()
        notify.act = act

        for _id in slot_ids:
            notify_formation = notify.formation.add()
            notify_formation.slot_id = _id

            try:
                data = self.doc['slots'][str(_id)]
            except KeyError:
                notify_formation.status = FORMATION_SLOT_NOT_OPEN
            else:
                notify_formation.position = self.doc['position'].index(_id)

                if not data['staff_id']:
                    notify_formation.status = FORMATION_SLOT_EMPTY
                else:
                    notify_formation.status = FORMATION_SLOT_USE
                    notify_formation.staff_id = data['staff_id']
                    notify_formation.unit_id = data['unit_id']

        MessagePipe(self.char_id).put(msg=notify)
