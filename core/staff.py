# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       staff
Date Created:   2015-07-09 17:07
Description:

"""

import random
import arrow

from dianjing.exception import GameException

from core.abstract import AbstractStaff
from core.mongo import MongoStaff, MongoStaffRecruit
from core.resource import money_text_to_item_id, ResourceClassification, STAFF_EXP_POOL_ID
from core.bag import Bag, TYPE_EQUIPMENT, get_item_type
from core.value_log import (
    ValueLogStaffRecruitTimes,
    ValueLogStaffRecruitScore,
    ValueLogStaffRecruitGoldFreeTimes,
    ValueLogStaffRecruitDiamondTimes,
    ValueLogStaffRecruitGoldTimes,
    ValueLogStaffStarUpTimes,
    ValueLogStaffLevelUpTimes,
)

# from core.signals import recruit_staff_signal, staff_level_up_signal
from core.signals import staff_new_add_signal

from config import (
    ConfigStaffRecruit,
    ConfigErrorMessage,
    ConfigItemNew,
    ConfigStaffNew,
    ConfigStaffStar,
    ConfigStaffLevelNew,
    ConfigEquipmentNew,
    ConfigStaffEquipmentAddition,
)

from utils.functional import make_string_id
from utils.message import MessagePipe

from protomsg.bag_pb2 import EQUIP_DECORATION, EQUIP_KEYBOARD, EQUIP_MONITOR, EQUIP_MOUSE
from protomsg.staff_pb2 import StaffRecruitNotify, StaffNotify, StaffRemoveNotify
from protomsg.staff_pb2 import RECRUIT_DIAMOND, RECRUIT_GOLD, RECRUIT_MODE_1, RECRUIT_MODE_2
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE

GOLD_MAX_FREE_TIMES = 5
GOLD_CD_SECONDS = 600
DIAMOND_CD_SECONDS = 3600 * 24 * 2

RECRUIT_CD_SECONDS = {
    1: 600,
    2: 3600 * 24 * 2
}


class RecruitResult(object):
    __slots__ = ['point', 'add_score', 'items']

    def __init__(self, point):
        self.point = point
        self.add_score = 0
        self.items = []

    def add(self, res):
        """

        :param res:
        :type res: config.staff.RecruitResult
        """
        self.add_score += res.score
        self.point += res.point
        if self.point < 0:
            self.point = 0

        for item in res.item:
            self.items.append(item)

    def items_for_save(self):
        result = {}
        for _id, _amount in self.items:
            if _id in result:
                result[_id] += _amount
            else:
                result[_id] = _amount

        return result.items()


class StaffRecruit(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.doc = MongoStaffRecruit.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoStaffRecruit.document()
            self.doc['_id'] = self.char_id
            self.doc['score'] = 0
            self.doc['point'] = {'1': 0, '2': 0}
            self.doc['recruit_at'] = {'1': 0, '2': 0}
            MongoStaffRecruit.db(self.server_id).insert_one(self.doc)

    @property
    def gold_free_times(self):
        today_times = ValueLogStaffRecruitGoldFreeTimes(self.server_id, self.char_id).count_of_today()
        free_times = GOLD_MAX_FREE_TIMES - today_times
        if free_times < 0:
            free_times = 0

        return free_times

    def get_cd_seconds(self, tp):
        now = arrow.utcnow().timestamp
        passed = now - self.doc['recruit_at'].get(str(tp), 0)
        cd = RECRUIT_CD_SECONDS[tp] - passed

        if cd < 0:
            return 0

        return cd

    def get_score(self):
        return self.doc['score']

    def get_point(self, tp):
        return self.doc['point'].get(str(tp), 0)

    def get_times(self, tp):
        return ValueLogStaffRecruitTimes(self.server_id, self.char_id).count(sub_id=tp)

    def recruit(self, tp, mode):
        if tp not in [RECRUIT_GOLD, RECRUIT_DIAMOND]:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if mode not in [RECRUIT_MODE_1, RECRUIT_MODE_2]:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if tp == RECRUIT_GOLD:
            if mode == RECRUIT_MODE_1:
                recruit_times = self._recruit_tp_1_mode_1()
            else:
                recruit_times = self._recruit_tp_1_mode_2()

            ValueLogStaffRecruitGoldTimes(self.server_id, self.char_id).record(value=recruit_times)
        else:
            if mode == RECRUIT_MODE_1:
                recruit_times = self._recruit_tp_2_mode_1()
            else:
                recruit_times = self._recruit_tp_2_mode_2()

            ValueLogStaffRecruitDiamondTimes(self.server_id, self.char_id).record(value=recruit_times)

        config = ConfigStaffRecruit.get(tp)
        current_times = self.get_times(tp) + 1

        result = RecruitResult(self.get_point(tp))

        for i in range(current_times, current_times + recruit_times):
            res = config.recruit(result.point, i)
            result.add(res)

        self.doc['point'][str(tp)] = result.point

        # 记录次数
        ValueLogStaffRecruitTimes(self.server_id, self.char_id).record(sub_id=tp, value=recruit_times)

        # 处理积分
        today_score = ValueLogStaffRecruitScore(self.server_id, self.char_id).count_of_today(sub_id=tp)
        can_add_score = config.reward_score_day_limit - today_score
        if can_add_score <= 0:
            # 今天获得的积分已经达到上限
            result.add_score = 0
        else:
            if result.add_score > can_add_score:
                # 要添加的，大于了 能添加的
                result.add_score = can_add_score

        self.doc['score'] += result.add_score
        ValueLogStaffRecruitScore(self.server_id, self.char_id).record(sub_id=tp, value=can_add_score)

        MongoStaffRecruit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'point.{0}'.format(tp): result.point,
                'score': self.doc['score']
            }}
        )

        resource_classify = ResourceClassification.classify(result.items_for_save())
        resource_classify.add(self.server_id, self.char_id)

        self.send_notify()
        # NOTE: 结果不能堆叠
        return result.items

    def _recruit_tp_1_mode_1(self):
        # 金币单抽
        config = ConfigStaffRecruit.get(1)

        def _remove_money():
            cost = [(money_text_to_item_id('gold'), config.cost_value_1)]

            resource_classify = ResourceClassification.classify(cost)
            resource_classify.check_exist(self.server_id, self.char_id)
            resource_classify.remove(self.server_id, self.char_id)

        if not self.gold_free_times:
            # 没有免费次数了， 就不判断CD，直接扣钱
            _remove_money()
        else:
            # 有免费次数，先判断是否在CD中，
            cd_seconds = self.get_cd_seconds(1)
            if cd_seconds:
                # 在CD中，扣钱
                _remove_money()
            else:
                # 免费的
                # 设置免费次数， 和时间戳
                self.doc['recruit_at']['1'] = arrow.utcnow().timestamp

                MongoStaffRecruit.db(self.server_id).update_one(
                    {'_id': self.char_id},
                    {'$set': {
                        'recruit_at.1': self.doc['recruit_at']['1']
                    }}
                )

                ValueLogStaffRecruitGoldFreeTimes(self.server_id, self.char_id).record()

        return 1

    def _recruit_tp_1_mode_2(self):
        # 金币十连抽
        config = ConfigStaffRecruit.get(1)

        cost = [(money_text_to_item_id('gold'), config.cost_value_1)]

        resource_classify = ResourceClassification.classify(cost)
        resource_classify.check_exist(self.server_id, self.char_id)
        resource_classify.remove(self.server_id, self.char_id)

        return 10

    def _recruit_tp_2_mode_1(self):
        # 钻石单抽
        config = ConfigStaffRecruit.get(2)

        cd_seconds = self.get_cd_seconds(2)
        if cd_seconds:
            cost = [(money_text_to_item_id('diamond'), config.cost_value_10)]

            resource_classify = ResourceClassification.classify(cost)
            resource_classify.check_exist(self.server_id, self.char_id)
            resource_classify.remove(self.server_id, self.char_id)
        else:
            self.doc['recruit_at']['2'] = arrow.utcnow().timestamp

            MongoStaffRecruit.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'recruit_at.2': self.doc['recruit_at']['2']
                }}
            )

        return 1

    def _recruit_tp_2_mode_2(self):
        # 钻石十连抽
        config = ConfigStaffRecruit.get(2)

        cost = [(money_text_to_item_id('diamond'), config.cost_value_10)]

        resource_classify = ResourceClassification.classify(cost)
        resource_classify.check_exist(self.server_id, self.char_id)
        resource_classify.remove(self.server_id, self.char_id)

        return 10

    def send_notify(self):
        notify = StaffRecruitNotify()
        notify.score = self.doc['score']
        for tp in [RECRUIT_GOLD, RECRUIT_DIAMOND]:
            notify_info = notify.info.add()
            notify_info.tp = tp
            notify_info.cd = self.get_cd_seconds(tp)
            if tp == RECRUIT_GOLD:
                notify_info.cur_free_times = self.gold_free_times
                notify_info.max_free_times = GOLD_MAX_FREE_TIMES
            else:
                notify_info.next_times = 10 - (self.get_times(tp) % 10)

        MessagePipe(self.char_id).put(msg=notify)


###################################
STAFF_MAX_LEVEL = max(ConfigStaffLevelNew.INSTANCES.keys())
STAFF_MAX_STAR = max(ConfigStaffStar.INSTANCES.keys())
MIN_STAR_EXP = 1
MAX_STAR_EXP = 3
AVG_STAR_EXP = (MIN_STAR_EXP + MAX_STAR_EXP) / 2


class Staff(AbstractStaff):
    __slots__ = []

    def __init__(self, server_id, char_id, unique_id, data):
        super(Staff, self).__init__()

        self.server_id = server_id
        self.char_id = char_id

        self.id = unique_id
        self.oid = data['oid']
        self.level = data['level']
        self.step = data['step']
        self.star = data['star']
        self.level_exp = data['level_exp']
        self.star_exp = data['star_exp']

        self.equip_mouse = data['equip_mouse']
        self.equip_keyboard = data['equip_keyboard']
        self.equip_monitor = data['equip_monitor']
        self.equip_decoration = data['equip_decoration']

        self.after_init()

    def reset(self):
        # 重置到初始状态
        self.level = 1
        self.step = 0
        self.star = (ConfigItemNew.get(self.oid).quality - 1) * 10
        self.level_exp = 0
        self.star_exp = 0

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'staffs.{0}.level'.format(self.id): self.level,
                'staffs.{0}.step'.format(self.id): self.step,
                'staffs.{0}.star'.format(self.id): self.star,
                'staffs.{0}.level_exp'.format(self.id): self.level_exp,
                'staffs.{0}.star_exp'.format(self.id): self.star_exp,
            }}
        )

    def level_up(self, exp_pool, up_level):
        from core.club import get_club_property
        max_level = min(STAFF_MAX_LEVEL, get_club_property(self.server_id, self.char_id, 'level') * 2)
        if self.level >= max_level:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_ALREADY_MAX_LEVEL"))

        target_level = self.level + up_level
        if target_level > max_level:
            target_level = max_level

        while self.level < target_level:
            config = ConfigStaffLevelNew.get(self.level)
            up_need_exp = config.exp - self.level_exp

            if exp_pool < up_need_exp:
                return exp_pool

            exp_pool -= up_need_exp
            self.level += 1
            self.level_exp = 0

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'staffs.{0}.level'.format(self.id): self.level,
                'staffs.{0}.level_exp'.format(self.id): self.level_exp
            }}
        )

        self.calculate()
        self.make_cache()
        return exp_pool

    def step_up(self):
        if self.step >= self.config.max_step:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_ALREADY_MAX_STEP"))

        if self.level < self.config.steps[self.step].level_limit:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_LEVEL_NOT_ENOUGH"))

        using_items = self.config.steps[self.step].update_item_need
        resource_classified = ResourceClassification.classify(using_items)
        resource_classified.check_exist(self.server_id, self.char_id)
        resource_classified.remove(self.server_id, self.char_id)

        self.step += 1
        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {
                'staffs.{0}.step'.format(self.id): 1
            }}
        )

        # NOTE 升阶可能会导致 天赋技能 改变
        # 不仅会影响自己，可能（如果在阵型中）也会影响到其他选手
        # 所以这里不自己 calculate， 而是先让 club 重新 load staffs

    def star_up(self):
        if self.star >= STAFF_MAX_STAR:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_ALREADY_MAX_STAR"))

        star_config = ConfigStaffStar.get(self.star)
        using_items = [(star_config.need_item_id, star_config.need_item_amount)]

        resource_classified = ResourceClassification.classify(using_items)
        resource_classified.check_exist(self.server_id, self.char_id)
        resource_classified.remove(self.server_id, self.char_id)

        if random.randint(1, 100) <= 30:
            inc_exp = 6
        else:
            inc_exp = random.randint(1, 3)

        exp = self.star_exp + inc_exp
        while True:
            if self.star == STAFF_MAX_STAR:
                if exp >= ConfigStaffStar.get(self.star).exp:
                    exp = ConfigStaffStar.get(self.star).exp - 1

                break

            if exp < ConfigStaffStar.get(self.star).exp:
                break

            exp -= ConfigStaffStar.get(self.star).exp
            self.star += 1

        self.star_exp = exp

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'staffs.{0}.star'.format(self.id): self.star,
                'staffs.{0}.star_exp'.format(self.id): self.star_exp
            }}
        )

        self.calculate()
        self.make_cache()

    def equipment_change(self, bag_slot_id, tp):
        if not bag_slot_id:
            # 卸下
            bag_slot_id = ""
        else:
            # 更换
            bag = Bag(self.server_id, self.char_id)
            slot = bag.get_slot(bag_slot_id)

            # TODO error handle
            item_id = slot['item_id']
            if get_item_type(item_id) != TYPE_EQUIPMENT:
                raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

            equip_config = ConfigEquipmentNew.get(item_id)
            if equip_config.tp != tp:
                raise GameException(ConfigErrorMessage.get_error_id("EQUIPMENT_TYPE_NOT_MATCH"))

            if StaffManger(self.server_id, self.char_id).find_staff_id_by_equipment_slot_id(bag_slot_id):
                raise GameException(ConfigErrorMessage.get_error_id("EQUIPMENT_ON_OTHER_STUFF"))

        if tp == EQUIP_MOUSE:
            key = 'equip_mouse'
        elif tp == EQUIP_KEYBOARD:
            key = 'equip_keyboard'
        elif tp == EQUIP_MONITOR:
            key = 'equip_monitor'
        else:
            key = 'equip_decoration'

        setattr(self, key, bag_slot_id)
        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'staffs.{0}.{1}'.format(self.id, key): bag_slot_id
            }}
        )

        self.calculate()
        self.make_cache()

    def add_equipment_property(self):
        bag = Bag(self.server_id, self.char_id)

        level = 0
        qualities = []

        # 装备本身属性
        for slot_id in [self.equip_keyboard, self.equip_monitor, self.equip_mouse, self.equip_decoration]:
            if not slot_id:
                continue

            data = bag.get_slot(slot_id)
            config = ConfigItemNew.get(data['item_id'])

            equip_config = ConfigEquipmentNew.get(data['item_id'])
            this_level = equip_config.levels[data['level']]

            self.attack += this_level.attack
            self.attack_percent += this_level.attack_percent
            self.defense += this_level.defense
            self.defense_percent += this_level.defense_percent
            self.manage += this_level.manage
            self.manage_percent += this_level.manage_percent
            self.operation += this_level.operation
            self.operation_percent += this_level.operation_percent

            if slot_id != self.equip_decoration:
                # 装备加成不算 饰品
                level += data['level']
                qualities.append(config.quality)

        # 装备加成
        equip_level_addition = ConfigStaffEquipmentAddition.get_by_level(level)
        if equip_level_addition:
            self.attack += equip_level_addition.attack
            self.attack_percent += equip_level_addition.attack_percent
            self.defense += equip_level_addition.defense
            self.defense_percent += equip_level_addition.defense_percent
            self.manage += equip_level_addition.manage
            self.manage_percent += equip_level_addition.manage_percent

        if len(qualities) == 3:
            equip_quality_addition = ConfigStaffEquipmentAddition.get_by_quality(min(qualities))
            if equip_quality_addition:
                self.attack += equip_quality_addition.attack
                self.attack_percent += equip_quality_addition.attack_percent
                self.defense += equip_quality_addition.defense
                self.defense_percent += equip_quality_addition.defense_percent
                self.manage += equip_quality_addition.manage
                self.manage_percent += equip_quality_addition.manage_percent

    def get_total_level_exp(self, percent=100):
        # 得到一路升级过来的经验
        exp = self.level_exp
        for i in range(self.level - 1, 0, -1):
            exp += ConfigStaffLevelNew.get(i).exp

        exp *= 1 + percent / 100.0
        return int(exp)

    def send_notify(self):
        notify = StaffNotify()
        notify.act = ACT_UPDATE
        notify_staff = notify.staffs.add()
        notify_staff.MergeFrom(self.make_protomsg())
        MessagePipe(self.char_id).put(msg=notify)


class StaffManger(object):
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoStaff.exist(self.server_id, self.char_id):
            doc = MongoStaff.document()
            doc['_id'] = self.char_id
            MongoStaff.db(server_id).insert_one(doc)

    @property
    def staffs_amount(self):
        # type: () -> int
        return len(self.get_staffs_data())

    def add_exp_pool(self, exp):
        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {
                'exp_pool': exp
            }}
        )

        self.send_notify(ids=[])

    def get_staffs_data(self, ids=None):
        """

        :rtype: dict[str, dict]
        """
        if ids:
            projection = {'staffs.{0}'.format(i): 1 for i in ids}
        else:
            projection = {'staffs': 1}

        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, projection)
        return doc['staffs']

    def find_staff_id_with_equip(self, bag_slot_id):
        keys = ['equip_mouse', 'equip_keyboard', 'equip_monitor', 'equip_decoration']

        staffs = self.get_staffs_data()
        for k, v in staffs.iteritems():
            for key in keys:
                if v.get(key, "") == bag_slot_id:
                    return k

        return None

    def get_all_staff_object(self):
        # type: () -> dict[str, Staff]
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, {'staffs': 1})
        return {k: self.get_staff_object(k) for k, _ in doc['staffs'].iteritems()}

    def get_staff_object(self, _id):
        """

        :param _id:
        :rtype : Staff | None
        """
        from core.club import Club

        obj = Staff.get(_id)
        if obj:
            return obj

        Club(self.server_id, self.char_id, load_staffs=False).force_load_staffs()
        return Staff.get(_id)

    def has_staff(self, ids):
        # type: (list[str]) -> bool
        # unique id
        projection = {'staffs.{0}'.format(i): 1 for i in ids}
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, projection)
        if not doc:
            return False

        staffs = doc.get('staffs', {})
        return len(ids) == len(staffs)

    def check_staff(self, ids):
        if not self.has_staff(ids):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

    def check_original_staff_is_initial_state(self, originals):
        # 原始ID， 并且匹配原始属性
        # originals: [(oid, amount)...]
        oids = []
        for _oid, _amount in originals:
            oids.extend([_oid] * _amount)

        staffs = self.get_all_staff_object().values()
        """:type: list[Staff]"""
        for s in staffs:
            for i in oids:
                if s.oid == i and s.is_initial_state():
                    oids.remove(i)
                    break

        if oids:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

    def add(self, staff_original_id, send_notify=True):
        if not ConfigStaffNew.get(staff_original_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        quality = ConfigItemNew.get(staff_original_id).quality

        unique_id = make_string_id()
        doc = MongoStaff.document_staff()
        doc['oid'] = staff_original_id
        doc['star'] = (quality - 1) * 10

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'staffs.{0}'.format(unique_id): doc}},
        )

        if send_notify:
            self.send_notify(ids=[unique_id])

        staff_new_add_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            oid=staff_original_id,
            unique_id=unique_id
        )

        return unique_id

    def remove(self, staff_id):

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$unset': {'staffs.{0}'.format(staff_id): 1}}
        )

        notify = StaffRemoveNotify()
        notify.ids.append(staff_id)
        MessagePipe(self.char_id).put(msg=notify)

    def remove_initial_state_staff(self, oid):
        staffs = self.get_all_staff_object().values()
        """:type: list[Staff]"""
        for s in staffs:
            if s.oid == oid and s.is_initial_state():
                self.remove(s.id)
                return

    def find_staff_id_by_equipment_slot_id(self, slot_id):
        # type: (str) -> str|None
        # 找slot_id在哪个角色身上
        assert slot_id, "Invalid slot_id: {0}".format(slot_id)
        doc = MongoStaff.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'staffs': 1}
        )

        for k, v in doc['staffs'].iteritems():
            if v['equip_mouse'] == slot_id or \
                            v['equip_keyboard'] == slot_id or \
                            v['equip_monitor'] == slot_id or \
                            v['equip_decoration'] == slot_id:
                return k

        return None

    def after_staff_change(self):
        from core.club import Club
        Club(self.server_id, self.char_id).send_notify()

    def equipment_change(self, staff_id, slot_id, tp):
        if tp not in [EQUIP_MOUSE, EQUIP_KEYBOARD, EQUIP_MONITOR, EQUIP_DECORATION]:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        staff = self.get_staff_object(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        staff.equipment_change(slot_id, tp)
        self.send_notify(ids=[staff_id])
        self.after_staff_change()

    def level_up(self, staff_id, up_level):
        staff = self.get_staff_object(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        doc = MongoStaff.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'exp_pool': 1}
        )

        exp_pool = doc.get('exp_pool', 0)
        remained_exp_pool = staff.level_up(exp_pool, up_level)

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'exp_pool': remained_exp_pool
            }}
        )

        self.send_notify(ids=[staff_id])
        ValueLogStaffLevelUpTimes(self.server_id, self.char_id).record()
        self.after_staff_change()


    def step_up(self, staff_id):
        from core.club import Club
        from core.formation import Formation
        staff = self.get_staff_object(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        staff.step_up()
        in_formation_staff_ids = Formation(self.server_id, self.char_id).in_formation_staffs().keys()
        if staff.id in in_formation_staff_ids:
            Club(self.server_id, self.char_id, load_staffs=False).force_load_staffs()
            self.send_notify(ids=in_formation_staff_ids)
        else:
            staff.calculate()
            staff.make_cache()
            self.send_notify(ids=[staff_id])

        self.after_staff_change()

    def star_up(self, staff_id):
        staff = self.get_staff_object(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        staff.star_up()
        ValueLogStaffStarUpTimes(self.server_id, self.char_id).record()
        self.send_notify(ids=[staff_id])
        self.after_staff_change()

    def destroy(self, staff_id, tp):
        from core.club import Club
        from core.formation import Formation

        if Formation(self.server_id, self.char_id).is_staff_in_formation(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_CANNOT_DESTROY_IN_FORMATION"))

        staff = self.get_staff_object(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        if tp == 0:
            # 普通分解
            items = [
                (STAFF_EXP_POOL_ID, staff.get_total_level_exp(70)),
                (money_text_to_item_id('crystal'), ConfigStaffNew.get(staff.oid).crystal)
            ]
        else:
            if staff.is_initial_state():
                raise GameException(ConfigErrorMessage.get_error_id("STAFF_CANNOT_DESTROY_INITIAL_STATE"))

            # TODO diamond count
            resource_classified = ResourceClassification.classify([(money_text_to_item_id('diamond'), 50)])
            resource_classified.check_exist(self.server_id, self.char_id)
            resource_classified.remove(self.server_id, self.char_id)

            items = [
                (STAFF_EXP_POOL_ID, staff.get_total_level_exp(100))
            ]

        resource_classified = ResourceClassification.classify(items)
        resource_classified.add(self.server_id, self.char_id)

        if tp == 0:
            self.remove(staff_id)
        else:
            staff.reset()
            in_formation_staff_ids = Formation(self.server_id, self.char_id).in_formation_staffs().keys()
            if staff.id in in_formation_staff_ids:
                Club(self.server_id, self.char_id, load_staffs=False).force_load_staffs()
                self.send_notify(ids=in_formation_staff_ids)
            else:
                staff.calculate()
                staff.make_cache()
                self.send_notify(ids=[staff_id])

        return resource_classified

    def send_notify(self, ids=None):
        if ids is None:
            projection = {'staffs': 1, 'exp_pool': 1}
            act = ACT_INIT
        else:
            if not ids:
                projection = {'staffs': 0}
            else:
                projection = {'staffs.{0}'.format(i): 1 for i in ids}
                projection['exp_pool'] = 1
            act = ACT_UPDATE

        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, projection)
        staffs = doc.get('staffs', {})

        notify = StaffNotify()
        notify.act = act
        notify.exp_pool = doc.get('exp_pool', 0)
        for k, _ in staffs.iteritems():
            notify_staff = notify.staffs.add()
            staff = self.get_staff_object(k)
            notify_staff.MergeFrom(staff.make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)
