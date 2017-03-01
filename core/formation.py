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

from core.resource import ResourceClassification

from utils.message import MessagePipe

from config import (
    ConfigErrorMessage,
    ConfigFormationSlot,
    ConfigFormation,
    ConfigUnitNew,
    ConfigQianBan,
    ConfigItemNew,
)

from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT
from protomsg.formation_pb2 import (
    FORMATION_SLOT_EMPTY,
    FORMATION_SLOT_NOT_OPEN,
    FORMATION_SLOT_USE,
    FormationSlot as MsgFormationSlot,
    FormationNotify,
    FormationSlotNotify,
)

MAX_SLOT_AMOUNT = 6

FORMATION_DEFAULT_POSITION = {
    1: [4],
    2: [7, 8],
    3: [1, 5, 4, 6, 2, 3],
    4: [1, 5, 4, 6, 2, 3],
    5: [1, 5, 4, 6, 2, 3],
    6: [1, 5, 4, 6, 2, 3],
}


class BaseFormation(object):
    __slots__ = ['server_id', 'char_id', 'doc']
    MONGO_COLLECTION = None

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.doc = self.get_or_create_doc()

    def get_or_create_doc(self):
        raise NotImplementedError()

    def get_slot_init_position(self, slot_amount):
        for pos in FORMATION_DEFAULT_POSITION[slot_amount]:
            if not self.doc['position'][pos]:
                return pos

        raise RuntimeError("Formation set position error. slot_id: {0}".format(slot_amount))

    def is_staff_in_formation(self, staff_id):
        for _, v in self.doc['slots'].iteritems():
            if v['staff_id'] and v['staff_id'] == staff_id:
                return True

        return False

    def in_formation_staffs(self):
        """

        :rtype: dict[str, dict]
        """

        # 如果没有兵种，这个选手在战斗中是不出现的
        # 但是一些天赋效果的条件是靠 上阵选手 来判断的
        # 所以这里得把所有在阵型中的选手返回
        # 没有兵种的slot，肯定没有position
        staffs = {}
        for slot_id, v in self.doc['slots'].iteritems():
            if v['staff_id']:
                try:
                    position = self.doc['position'].index(int(slot_id))
                except ValueError:
                    position = -1

                staffs[v['staff_id']] = {
                    'unit_id': v['unit_id'],
                    'position': position,
                    'policy': v.get('policy', 1),
                    'slot_id': int(slot_id),
                }

        return staffs

    def working_staff_oids(self):
        from core.inspire import Inspire
        oids = []

        sm = StaffManger(self.server_id, self.char_id)
        # XXX: 这里不能用 get_staff_object
        # 因为get_staff_obj 可能用调用到 Club.force_load_staffs
        # 在 Club.force_load_staffs 中又会调用 这个方法
        # 然后就死循环了
        all_staffs = sm.get_staffs_data()

        working_staffs = self.in_formation_staffs().keys()
        working_staffs.extend(Inspire(self.server_id, self.char_id).all_staffs())

        for s in working_staffs:
            oids.append(all_staffs[s]['oid'])

        return oids

    def set_staff(self, slot_id, staff_id):
        from core.inspire import Inspire

        if str(slot_id) not in self.doc['slots']:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_SLOT_NOT_OPEN"))

        sm = StaffManger(self.server_id, self.char_id)
        sm.check_staff(ids=[staff_id])

        Inspire(self.server_id, self.char_id).check_staff_in(staff_id)

        this_staff_obj = sm.get_staff_object(staff_id)

        in_formation_staffs = self.in_formation_staffs()
        for k, v in in_formation_staffs.iteritems():
            if k == staff_id:
                raise GameException(ConfigErrorMessage.get_error_id("FORMATION_STAFF_ALREADY_IN"))

            if v['slot_id'] != slot_id and sm.get_staff_object(k).oid == this_staff_obj.oid:
                # 其他位置 不能上 oid 一样的人
                # 但是这个slot替换就可以
                raise GameException(ConfigErrorMessage.get_error_id("FORMATION_STAFF_ALREADY_IN"))

        old_staff_id = self.doc['slots'][str(slot_id)]['staff_id']
        self.doc['slots'][str(slot_id)]['staff_id'] = staff_id
        self.doc['slots'][str(slot_id)]['unit_id'] = 0
        self.doc['slots'][str(slot_id)]['policy'] = 1

        updater = {
            'slots.{0}.staff_id'.format(slot_id): staff_id,
            'slots.{0}.unit_id'.format(slot_id): 0,
            'slots.{0}.policy'.format(slot_id): 1
        }

        if slot_id in self.doc['position']:
            # 换完人，兵种清空了，也就从阵型位置上撤掉了
            index = self.doc['position'].index(slot_id)
            self.doc['position'][index] = 0

            updater['position.{0}'.format(index)] = 0

        self.MONGO_COLLECTION.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        return old_staff_id

    def set_unit(self, slot_id, unit_id):
        if str(slot_id) not in self.doc['slots']:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_SLOT_NOT_OPEN"))

        UnitManager(self.server_id, self.char_id).check_unit_unlocked(unit_id)

        staff_id = self.doc['slots'][str(slot_id)]['staff_id']
        if not staff_id:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_SLOT_NO_STAFF"))

        s = StaffManger(self.server_id, self.char_id).get_staff_object(staff_id)

        config_qianban = ConfigQianBan.get(s.oid)
        if not config_qianban:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        allowed_unit_ids = []
        for k, v in config_qianban.info.iteritems():
            if v.condition_tp == 1:
                # 装备兵种
                allowed_unit_ids.extend(v.condition_value)

        if unit_id not in allowed_unit_ids:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        # u = UnitManager(self.server_id, self.char_id).get_unit_object(unit_id)
        # if s.config.race != u.config.race:
        #     raise GameException(ConfigErrorMessage.get_error_id("FORMATION_STAFF_UNIT_RACE_NOT_MATCH"))

        self.doc['slots'][str(slot_id)]['unit_id'] = unit_id
        self.doc['slots'][str(slot_id)]['policy'] = 1

        updater = {
            'slots.{0}.unit_id'.format(slot_id): unit_id,
            'slots.{0}.policy'.format(slot_id): 1
        }

        # 如果没有位置，那么就给设置一个位置
        if slot_id not in self.doc['position']:
            position = self.get_slot_init_position(len(self.doc['slots']))
            self.doc['position'][position] = slot_id
            updater['position.{0}'.format(position)] = slot_id

        self.MONGO_COLLECTION.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

    def sync_slots(self, slots_data):
        positions = [0] * 30
        updater = {}

        for slot_id, index, policy in slots_data:
            if str(slot_id) not in self.doc['slots']:
                raise GameException(ConfigErrorMessage.get_error_id("FORMATION_SLOT_NOT_OPEN"))

            if index < 0 or index > 29:
                raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

            if policy not in [1, 2]:
                raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

            if not self.doc['slots'][str(slot_id)]['staff_id']:
                raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

            positions[index] = slot_id
            updater['slots.{0}.policy'.format(slot_id)] = policy

        # # 发来的只是部分数据，对应以前的position中的数据 要得意保留
        # # 比如 以前的 position 是 [0, 1, 0, 2, 0]
        # # 发来的数据是 把 1 移动到 最后
        # # 这时候自己组织的 positions 是 [0, 0, 0, 0, 1]
        # # 现在就需要把 2 有也放进来
        # for _index, _id in enumerate(self.doc['position']):
        #     if _id not in positions:
        #         if positions[_index]:
        #             raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))
        #
        #         positions[_index] = _id

        updater['position'] = positions

        self.doc['position'] = positions
        for slot_id, index, policy in slots_data:
            self.doc['slots'][str(slot_id)]['policy'] = policy

        self.MONGO_COLLECTION.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )


class Formation(BaseFormation):
    __slots__ = []
    MONGO_COLLECTION = MongoFormation

    def get_or_create_doc(self):
        doc = self.MONGO_COLLECTION.db(self.server_id).find_one({'_id': self.char_id})
        if not doc:
            doc = self.MONGO_COLLECTION.document()
            doc['_id'] = self.char_id
            doc['position'] = [0] * 9
            self.MONGO_COLLECTION.db(self.server_id).insert_one(doc)

        return doc

    def initialize(self, init_data):
        # [(staff_unique_id, unit_id), ...]

        opened_slot_ids = ConfigFormationSlot.get_opened_slot_ids([])

        updater = {}
        for index, (staff_unique_id, unit_id) in enumerate(init_data):
            slot_id = opened_slot_ids[index]

            doc = self.MONGO_COLLECTION.document_slot()
            doc['staff_id'] = staff_unique_id
            doc['unit_id'] = unit_id

            self.doc['slots'][str(slot_id)] = doc

            position = self.get_slot_init_position(len(self.doc['slots']))
            self.doc['position'][position] = slot_id

            updater['slots.{0}'.format(slot_id)] = doc
            updater['position.{0}'.format(position)] = slot_id

        self.MONGO_COLLECTION.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

    def try_open_slots(self):
        from core.challenge import Challenge

        passed_challenge_ids = Challenge(self.server_id, self.char_id).get_passed_challenge_ids()
        opened_slot_ids = ConfigFormationSlot.get_opened_slot_ids(passed_challenge_ids)

        new_slot_ids = []
        updater = {}

        for i in opened_slot_ids:
            if str(i) in self.doc['slots']:
                continue

            doc = self.MONGO_COLLECTION.document_slot()
            doc['staff_id'] = ""
            doc['unit_id'] = 0

            self.doc['slots'][str(i)] = doc

            updater['slots.{0}'.format(i)] = doc
            new_slot_ids.append(i)

        if new_slot_ids:
            self.MONGO_COLLECTION.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': updater}
            )

            self.send_slot_notify(slot_ids=new_slot_ids)

    def set_staff(self, slot_id, staff_id):
        old_staff_id = super(Formation, self).set_staff(slot_id, staff_id)
        # 检测阵型是否还可用
        if self.doc['using'] and not self.is_formation_valid(self.doc['using']):
            self.use_formation(0)
        else:
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

        return old_staff_id

    def set_unit(self, slot_id, unit_id):
        super(Formation, self).set_unit(slot_id, unit_id)
        # 检测阵型是否还可用
        if self.doc['using'] and not self.is_formation_valid(self.doc['using']):
            self.use_formation(0)
        else:
            self.send_slot_notify(slot_ids=[slot_id])

            # NOTE 兵种改变可能会导致牵绊改变，从而改变天赋
            # 所以这里暴力重新加载staffs
            club = Club(self.server_id, self.char_id, load_staffs=False)
            club.force_load_staffs(send_notify=True)

    def sync_slots(self, slots_data):
        super(Formation, self).sync_slots(slots_data)

        self.send_slot_notify(slot_ids=self.doc['slots'].keys())

        # 阵型改变，从而改变天赋
        # 所以这里暴力重新加载staffs
        club = Club(self.server_id, self.char_id, load_staffs=False)
        club.force_load_staffs(send_notify=True)

    def active_formation(self, fid):
        from core.challenge import Challenge

        config = ConfigFormation.get(fid)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_NOT_EXIST"))

        if str(fid) in self.doc['levels']:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_ALREADY_ACTIVE"))

        Challenge(self.server_id, self.char_id).check_starts(config.active_need_star)

        rc = ResourceClassification.classify(config.active_need_items)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id, message="Formation.active_formation:{0}".format(fid))

        self.doc['levels'][str(fid)] = 1
        self.MONGO_COLLECTION.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'levels.{0}'.format(fid): 1
            }}
        )

        self.send_formation_notify(formation_ids=[fid])

    def levelup_formation(self, fid):
        from core.challenge import Challenge

        config = ConfigFormation.get(fid)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_NOT_EXIST"))

        level = self.doc['levels'].get(str(fid), 0)
        if level == 0:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_NOT_ACTIVE"))

        if level >= config.max_level:
            raise GameException(ConfigErrorMessage.get_error_id("FORMATION_REACH_MAX_LEVEL"))

        Challenge(self.server_id, self.char_id).check_starts(config.levels[level].level_up_need_star)

        rc = ResourceClassification.classify(config.levels[level].level_up_need_items)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id, message="Formation.levelup_formation:{0}".format(fid))

        self.doc['levels'][str(fid)] = level + 1
        self.MONGO_COLLECTION.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'levels.{0}'.format(fid): level + 1
            }}
        )

        self.send_formation_notify(formation_ids=[fid])

        if fid == self.doc['using']:
            # 阵型改变，从而改变天赋
            # 所以这里暴力重新加载staffs
            club = Club(self.server_id, self.char_id, load_staffs=False)
            club.force_load_staffs(send_notify=True)

    def is_formation_valid(self, fid):
        use_condition_type, use_condition_value = ConfigFormation.get(fid).use_condition
        in_formation_staffs = self.in_formation_staffs()

        if use_condition_type == 0:
            # 任意数量
            amount = 0
            for _, v in in_formation_staffs.iteritems():
                if v['unit_id']:
                    amount += 1

            if amount < use_condition_value:
                return False
        else:
            # 对应种族数量
            # 因为这个的 condition_type 的定义 和 race 定义是一样的，所以直接比较
            amount = 0
            for _, v in in_formation_staffs.iteritems():
                if not v['unit_id']:
                    continue

                if ConfigUnitNew.get(v['unit_id']).race == use_condition_type:
                    amount += 1

            if amount < use_condition_value:
                return False

        return True

    def use_formation(self, fid):
        if fid != 0:
            config = ConfigFormation.get(fid)
            if not config:
                raise GameException(ConfigErrorMessage.get_error_id("FORMATION_NOT_EXIST"))

            level = self.doc['levels'].get(str(fid), 0)
            if level == 0:
                raise GameException(ConfigErrorMessage.get_error_id("FORMATION_NOT_ACTIVE"))

            if not self.is_formation_valid(fid):
                raise GameException(ConfigErrorMessage.get_error_id("FORMATION_CAN_NOT_USE"))

        updater = {'using': fid}
        self.doc['using'] = fid
        # 把格子策略设置为默认值
        for k in self.doc['slots']:
            self.doc['slots'][k]['policy'] = 1
            updater['slots.{0}.policy'.format(k)] = 1

        self.MONGO_COLLECTION.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_slot_notify(slot_ids=self.doc['slots'].keys())
        self.send_formation_notify(formation_ids=[])

        # 阵型改变，从而改变天赋
        # 所以这里暴力重新加载staffs
        club = Club(self.server_id, self.char_id, load_staffs=False)
        club.force_load_staffs(send_notify=True)

    def get_talent_effects(self):
        fid = self.doc['using']
        if not fid:
            return []

        level = self.doc['levels'][str(fid)]
        return ConfigFormation.get(fid).levels[level].talent_effects

    def _get_value_for_task_condition(self):
        # 给任务条件用的
        # 要求上阵6人，每人都要有 键盘，鼠标，显示器装备
        from core.bag import Bag

        staffs = self.in_formation_staffs().keys()
        if len(staffs) < 6:
            return 0, 0

        qualities = []
        levels = []
        sm = StaffManger(self.server_id, self.char_id)
        bag = Bag(self.server_id, self.char_id)

        for sid in staffs:
            obj = sm.get_staff_object(sid)
            for bag_slot_id in [obj.equip_keyboard, obj.equip_mouse, obj.equip_monitor]:
                if not bag_slot_id:
                    return 0, 0

                item_data = bag.get_slot(bag_slot_id)
                qualities.append(ConfigItemNew.get(item_data['item_id']).quality)
                levels.append(item_data['level'])

        return min(qualities), min(levels)

    def get_min_equipment_quality_for_task_condition(self):
        q, l = self._get_value_for_task_condition()
        return q

    def get_min_equipment_level_for_task_condition(self):
        q, l = self._get_value_for_task_condition()
        return l

    def make_slot_msg(self, slot_ids=None):
        if not slot_ids:
            slot_ids = range(1, MAX_SLOT_AMOUNT + 1)

        sm = StaffManger(self.server_id, self.char_id)

        msgs = []
        for _id in slot_ids:
            msg_slot = MsgFormationSlot()
            msg_slot.slot_id = int(_id)

            try:
                data = self.doc['slots'][str(_id)]
            except KeyError:
                msg_slot.status = FORMATION_SLOT_NOT_OPEN
            else:
                if not data['staff_id']:
                    msg_slot.status = FORMATION_SLOT_EMPTY
                else:
                    msg_slot.status = FORMATION_SLOT_USE
                    msg_slot.staff_id = data['staff_id']
                    msg_slot.unit_id = data['unit_id']
                    if data['unit_id']:
                        msg_slot.position = self.doc['position'].index(int(_id))
                    else:
                        msg_slot.position = -1

                    msg_slot.staff_oid = sm.get_staff_object(data['staff_id']).oid
                    msg_slot.policy = data.get('policy', 1)

            msgs.append(msg_slot)

        return msgs

    def send_slot_notify(self, slot_ids=None):
        if slot_ids:
            act = ACT_UPDATE
        else:
            act = ACT_INIT
            slot_ids = range(1, MAX_SLOT_AMOUNT + 1)

        slot_msgs = self.make_slot_msg(slot_ids=slot_ids)

        notify = FormationSlotNotify()
        notify.act = act

        for _msg in slot_msgs:
            notify_slot = notify.slots.add()
            notify_slot.MergeFrom(_msg)

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
