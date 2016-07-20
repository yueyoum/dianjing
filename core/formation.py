# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       formation
Date Created:   2016-04-12 14-56
Description:

"""

from dianjing.exception import GameException

from core.mongo import MongoFormation
from core.staff import StaffManger
from core.unit import UnitManager
from core.club import Club
from core.challenge import Challenge
from core.resource import ResourceClassification

from utils.message import MessagePipe

from config import ConfigErrorMessage, ConfigFormationSlot, ConfigFormation

from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT
from protomsg.formation_pb2 import (
    FORMATION_SLOT_EMPTY,
    FORMATION_SLOT_NOT_OPEN,
    FORMATION_SLOT_USE,
    FormationNotify,
    FormationSlotNotify,
)

MAX_SLOT_AMOUNT = 6

FORMATION_DEFAULT_POSITION = {
    2: [9, 7],
    3: [7, 9, 6, 8, 10, 11],
    4: [20, 19, 21, 18, 22, 23],
    5: [20, 19, 21, 18, 22, 23],
    6: [20, 19, 21, 18, 22, 23],
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

    def get_slot_init_position(self, slot_id):
        for pos in FORMATION_DEFAULT_POSITION[slot_id]:
            this_pos_slot_id = self.doc['position'][pos]
            if this_pos_slot_id == slot_id:
                return pos

            if not this_pos_slot_id:
                return pos

        raise RuntimeError("Formation set position error. slot_id: {0}".format(slot_id))

    def initialize(self, init_data):
        # [(staff_unique_id, unit_id, position), ...]

        opened_slot_ids = ConfigFormationSlot.get_opened_slot_ids(1)

        updater = {}
        for index, (staff_unique_id, unit_id, position) in enumerate(init_data):
            slot_id = opened_slot_ids[index]

            doc = MongoFormation.document_slot()
            doc['staff_id'] = staff_unique_id
            doc['unit_id'] = unit_id

            self.doc['slots'][str(slot_id)] = doc
            self.doc['position'][position] = slot_id

            updater['slots.{0}'.format(slot_id)] = doc
            updater['position.{0}'.format(position)] = slot_id

        MongoFormation.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

    def try_open_slots(self, new_club_level):
        opened_slot_ids = ConfigFormationSlot.get_opened_slot_ids(new_club_level)

        new_slot_ids = []
        updater = {}

        for i in opened_slot_ids:
            if str(i) in self.doc['slots']:
                continue

            pos = self.get_slot_init_position(i)
            doc = MongoFormation.document_slot()
            doc['staff_id'] = ""
            doc['unit_id'] = 0

            self.doc['slots'][str(i)] = doc
            self.doc['position'][pos] = i

            updater['slots.{0}'.format(i)] = doc
            updater['position.{0}'.format(pos)] = i

            new_slot_ids.append(i)

        if new_slot_ids:
            MongoFormation.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': updater}
            )

            self.send_slot_notify(slot_ids=new_slot_ids)

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
            pos = self.get_slot_init_position(slot_id)
            old_pos = self.doc['position'].index(slot_id)
            if old_pos != pos:
                # 注意： 可能相同
                self.doc['position'][old_pos] = 0
                self.doc['position'][pos] = slot_id

                updater['position.{0}'.format(old_pos)] = 0
                updater['position.{0}'.format(pos)] = slot_id

        self.doc['slots'][str(slot_id)]['staff_id'] = staff_id
        self.doc['slots'][str(slot_id)]['unit_id'] = 0

        updater['slots.{0}.staff_id'.format(slot_id)] = staff_id
        updater['slots.{0}.unit_id'.format(slot_id)] = 0

        MongoFormation.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_slot_notify(slot_ids=[slot_id])

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

        self.send_slot_notify(slot_ids=[slot_id])

        u = UnitManager(self.server_id, self.char_id).get_unit_object(unit_id)
        s = StaffManger(self.server_id, self.char_id).get_staff_object(staff_id)
        s.set_unit(u)
        s.calculate()
        s.make_cache()

        # NOTE 兵种改变可能会导致牵绊改变，从而改变天赋
        # 所以这里暴力重新加载staffs
        club = Club(self.server_id, self.char_id, load_staffs=False)
        club.force_load_staffs(send_notify=True)

    def set_policy(self, slot_id, policy):
        if str(slot_id) not in self.doc['slots']:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_SLOT_NOT_OPEN"))

        staff_id = self.doc['slots'][str(slot_id)]['staff_id']
        if not staff_id:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_SLOT_NO_STAFF"))

        if policy not in [1, 2]:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        self.doc['slots'][str(slot_id)]['policy'] = policy
        MongoFormation.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'slots.{0}.policy'.format(slot_id): policy
            }}
        )
        self.send_slot_notify(slot_ids=[slot_id])

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

        self.send_slot_notify(slot_ids=changed)
        # 阵型位置改了，staff有缓存，得重新load
        Club(self.server_id, self.char_id, load_staffs=False).force_load_staffs()

    def active_formation(self, fid):
        config = ConfigFormation.get(fid)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_NOT_EXIST"))

        if str(fid) in self.doc['levels']:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_ALREADY_ACTIVE"))

        Challenge(self.server_id, self.char_id).check_starts(config.active_need_star)

        rc = ResourceClassification.classify(config.active_need_items)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id)

        self.doc['levels'][str(fid)] = 1
        MongoFormation.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'levels.{0}'.format(fid): 1
            }}
        )

        self.send_formation_notify(formation_ids=[fid])

    def levelup_formation(self, fid):
        config = ConfigFormation.get(fid)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_NOT_EXIST"))

        level = self.doc['levels'].get(str(fid), 0)
        if level == 0:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_NOT_ACTIVE"))

        if level >= config.max_level:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_REACH_MAX_LEVEL"))

        Challenge(self.server_id, self.char_id).check_starts(config.levels[level].level_up_need_star)

        self.doc['levels'][str(fid)] = level + 1
        MongoFormation.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'levels.{0}'.format(fid): level + 1
            }}
        )

        self.send_formation_notify(formation_ids=[fid])

    def is_formation_valid(self, fid):
        use_condition_type, use_condition_value = ConfigFormation.get(fid).use_condition

        in_formation_staffs = self.in_formation_staffs()
        sm = StaffManger(self.server_id, self.char_id)

        if use_condition_type == 0:
            # 任意数量
            if len(in_formation_staffs) < use_condition_value:
                return False
        else:
            # 对应种族数量
            # 因为这个的 condition_type 的定义 和 race 定义是一样的，所以直接比较
            amount = 0
            for staff_id in in_formation_staffs:
                if sm.get_staff_object(staff_id).config.race == use_condition_type:
                    amount += 1

            if amount < use_condition_value:
                return False

        return True

    def use_formation(self, fid):
        config = ConfigFormation.get(fid)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_NOT_EXIST"))

        level = self.doc['levels'].get(str(fid), 0)
        if level == 0:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_NOT_ACTIVE"))

        if not self.is_formation_valid(fid):
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_CAN_NOT_USE"))

        self.doc['using'] = fid
        MongoFormation.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'using': fid
            }}
        )

        self.send_formation_notify(formation_ids=[])

    def send_slot_notify(self, slot_ids=None):
        if slot_ids:
            act = ACT_UPDATE
        else:
            act = ACT_INIT
            slot_ids = range(1, MAX_SLOT_AMOUNT + 1)

        notify = FormationSlotNotify()
        notify.act = act

        for _id in slot_ids:
            notify_slot = notify.slots.add()
            notify_slot.slot_id = _id

            try:
                data = self.doc['slots'][str(_id)]
            except KeyError:
                notify_slot.status = FORMATION_SLOT_NOT_OPEN
            else:
                notify_slot.position = self.doc['position'].index(_id)

                if not data['staff_id']:
                    notify_slot.status = FORMATION_SLOT_EMPTY
                else:
                    notify_slot.status = FORMATION_SLOT_USE
                    notify_slot.staff_id = data['staff_id']
                    notify_slot.unit_id = data['unit_id']
                    notify_slot.policy = data.get('policy', 1)

        MessagePipe(self.char_id).put(msg=notify)

    def send_formation_notify(self, formation_ids=None):
        if formation_ids:
            act = ACT_UPDATE
        else:
            act = ACT_INIT
            formation_ids = ConfigFormation.INSTANCES.keys()

        notify = FormationNotify()
        notify.act = act
        notify.using_formation = self.doc['using']

        for i in formation_ids:
            notify_formation = notify.formation.add()
            notify_formation.id = i
            notify_formation.level = self.doc['levels'].get(str(i), 0)

        MessagePipe(self.char_id).put(msg=notify)
