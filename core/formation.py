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

FORMATION_DEFAULT_POSITION = {
    2: [20, 22],
    3: [22, 20, 23, 21, 19, 18],
    4: [9, 10, 8, 11, 7, 6],
    5: [9, 10, 8, 11, 7, 6],
    6: [9, 10, 8, 11, 7, 6],
}


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

    def initialize(self, init_data):
        # [(staff_unique_id, unit_id, position), ...]

        def _get_empty_position():
            empty_positions = [_index for _index, _slot_id in enumerate(self.doc['position']) if _slot_id == 0]
            return random.choice(empty_positions)

        slot_id = 1

        updater = {}
        for staff_unique_id, unit_id, position in init_data:
            doc = MongoFormation.document_slot()
            doc['staff_id'] = staff_unique_id
            doc['unit_id'] = unit_id

            self.doc['slots'][str(slot_id)] = doc
            self.doc['position'][position] = slot_id

            updater['slots.{0}'.format(slot_id)] = doc
            updater['position.{0}'.format(position)] = slot_id

            slot_id += 1

        more_open_slot_amount = MAX_SLOT_AMOUNT - len(init_data)
        for i in range(more_open_slot_amount):
            doc = MongoFormation.document_slot()
            doc['staff_id'] = ""
            doc['unit_id'] = 0

            self.doc['slots'][str(slot_id)] = doc

            pos = _get_empty_position()
            self.doc['position'][pos] = slot_id

            updater['slots.{0}'.format(slot_id)] = doc
            updater['position.{0}'.format(pos)] = slot_id

            slot_id += 1

        MongoFormation.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

    def is_staff_in_formation(self, staff_id):
        for _, v in self.doc['slots'].iteritems():
            if v['staff_id'] and v['staff_id'] == staff_id:
                return True

        return False

    def in_formation_staffs(self):
        """

        :rtype: dict[str, dict]
        """
        staffs = {}
        for slot_id, v in self.doc['slots'].iteritems():
            if v['staff_id']:
                position = self.doc['position'].index(int(slot_id))
                staffs[v['staff_id']] = {
                    'unit_id': v['unit_id'],
                    'position': position
                }

        return staffs

    def set_staff(self, slot_id, staff_id):
        if str(slot_id) not in self.doc['slots']:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_SLOT_NOT_OPEN"))

        StaffManger(self.server_id, self.char_id).check_staff(ids=[staff_id])

        if staff_id in self.in_formation_staffs():
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_STAFF_ALREADY_IN"))

        updater = {}

        old_staff_id = self.doc['slots'][str(slot_id)]['staff_id']
        if not old_staff_id:
            # 这是新上阵的选手，需要根据是第几个上的，确定其位置
            this_amount = len(self.in_formation_staffs()) + 1

            for pos in FORMATION_DEFAULT_POSITION[this_amount]:
                if not self.doc['position'][pos]:
                    break
            else:
                raise RuntimeError("Formation Auto set position error. now amount: {0}".format(this_amount))

            old_pos = self.doc['position'].index(slot_id)
            self.doc['position'][old_pos] = 0
            self.doc['position'][pos] = slot_id

            updater['position.{0}'.format(pos)] = slot_id
            updater['position.{0}'.format(old_pos)] = 0

        self.doc['slots'][str(slot_id)]['staff_id'] = staff_id
        self.doc['slots'][str(slot_id)]['unit_id'] = 0

        updater['slots.{0}.staff_id'.format(slot_id)] = staff_id
        updater['slots.{0}.unit_id'.format(slot_id)] = 0

        MongoFormation.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_notify(slot_ids=[slot_id])

        # NOTE 阵型改变，重新load staffs
        # 这里不直接调用 club.force_load_staffs 的 send_notify
        # 是因为这里 改变的staff 还可能包括下阵的
        changed_staff_ids = self.in_formation_staffs().keys()
        if old_staff_id:
            changed_staff_ids.append(old_staff_id)

        club = Club(self.server_id, self.char_id, load_staffs=False)
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

        # NOTE 兵种改变可能会导致牵绊改变，从而改变天赋
        # 所以这里暴力重新加载staffs
        club = Club(self.server_id, self.char_id, load_staffs=False)
        club.force_load_staffs(send_notify=True)

    def move_slot(self, slot_id, to_index):
        if str(slot_id) not in self.doc['slots']:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_SLOT_NOT_OPEN"))

        if to_index < 0 or to_index > 30:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        this_slot_index = self.doc['position'].index(slot_id)
        target_slot_id = self.doc['position'][to_index]

        self.doc['position'][to_index] = slot_id
        self.doc['position'][this_slot_index] = target_slot_id

        MongoFormation.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'position.{0}'.format(to_index): slot_id,
                'position.{0}'.format(this_slot_index): target_slot_id
            }}
        )

        changed = [slot_id]
        if target_slot_id:
            # NOTE: 要是 把 slot_id 移动到 一个空的位置
            # 此时 target_slot_id 为0， 直接发notify 就会混乱
            changed.append(target_slot_id)

        self.send_notify(slot_ids=changed)

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
