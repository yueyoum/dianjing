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
from core.bag import Bag, Equipment, TYPE_EQUIPMENT, get_item_type
from core.value_log import (
    ValueLogStaffRecruitTimes,
    ValueLogStaffRecruitScore,
    ValueLogStaffRecruitGoldFreeTimes,
    ValueLogStaffRecruitDiamondTimes,
    ValueLogStaffRecruitGoldTimes,
    ValueLogStaffStarUpTimes,
    ValueLogStaffLevelUpTimes,
)

from core.signals import (
    staff_new_add_signal,
    recruit_staff_diamond_signal,
    recruit_staff_gold_signal,
    staff_level_up_signal,
    staff_star_up_signal,
    staff_step_up_signal,
    task_condition_trig_signal,
)

from core import checker

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
from utils.stdvalue import MAX_INT

from protomsg.bag_pb2 import EQUIP_DECORATION, EQUIP_KEYBOARD, EQUIP_MONITOR, EQUIP_MOUSE, EQUIP_SPECIAL
from protomsg.staff_pb2 import StaffRecruitNotify, StaffNotify, StaffRemoveNotify
from protomsg.staff_pb2 import RECRUIT_DIAMOND, RECRUIT_GOLD, RECRUIT_MODE_1, RECRUIT_MODE_2
from protomsg.common_pb2 import (
    ACT_INIT,
    ACT_UPDATE,

    PROPERTY_STAFF_ATTACK_PERCENT,
    PROPERTY_STAFF_DEFENSE_PERCENT,
    PROPERTY_STAFF_MANAGE_PERCENT,
    PROPERTY_STAFF_OPERATION_PERCENT,

    PROPERTY_UNIT_HP_PERCENT,
    PROPERTY_UNIT_ATTACK_PERCENT,
    PROPERTY_UNIT_DEFENSE_PERCENT,
    PROPERTY_UNIT_HIT_PERCENT,
    PROPERTY_UNIT_DODGE_PERCENT,
    PROPERTY_UNIT_CRIT_PERCENT,
    PROPERTY_UNIT_TOUGHNESS_PERCENT,
    PROPERTY_UNIT_CRIT_MULTIPLE,

    PROPERTY_UNIT_HURT_ADDIITON_TO_TERRAN,
    PROPERTY_UNIT_HURT_ADDIITON_TO_PROTOSS,
    PROPERTY_UNIT_HURT_ADDIITON_TO_ZERG,
    PROPERTY_UNIT_HURT_ADDIITON_BY_TERRAN,
    PROPERTY_UNIT_HURT_ADDIITON_BY_PROTOSS,
    PROPERTY_UNIT_HURT_ADDIITON_BY_ZERG,
    PROPERTY_UNIT_FINAL_HURT_ADDITION,
    PROPERTY_UNIT_FINAL_HURT_REDUCE,
)

GOLD_MAX_FREE_TIMES = 5
GOLD_CD_SECONDS = 600

RECRUIT_CD_SECONDS = {
    1: 600,
    2: 3600 * 24
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

        self.items.extend(res.item)


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

    def add_score(self, value):
        self.doc['score'] += value
        MongoStaffRecruit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'score': self.doc['score']
            }}
        )
        self.send_notify()

    def check_score(self, value):
        new_score = self.doc['score'] - value
        if new_score < 0:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_RECRUIT_SCORE_NOT_ENOUGH"))

        return new_score

    def remove_score(self, value):
        new_score = self.check_score(value)
        self.doc['score'] = new_score
        MongoStaffRecruit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'score': new_score
            }}
        )

        self.send_notify()

    def get_point(self, tp):
        return self.doc['point'].get(str(tp), 0)

    def get_times(self, tp):
        return ValueLogStaffRecruitTimes(self.server_id, self.char_id).count(sub_id=tp)

    def recruit(self, tp, mode):
        if tp not in [RECRUIT_GOLD, RECRUIT_DIAMOND]:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if mode not in [RECRUIT_MODE_1, RECRUIT_MODE_2]:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        # NOTE: 钻石免费单抽 的积分 要单独处理
        diamond_single_free = False

        if tp == RECRUIT_GOLD:
            if mode == RECRUIT_MODE_1:
                recruit_times = self._recruit_tp_1_mode_1()
            else:
                recruit_times = self._recruit_tp_1_mode_2()

            ValueLogStaffRecruitGoldTimes(self.server_id, self.char_id).record(value=recruit_times)
        else:
            if mode == RECRUIT_MODE_1:
                recruit_times, diamond_single_free = self._recruit_tp_2_mode_1()
            else:
                recruit_times = self._recruit_tp_2_mode_2()

            ValueLogStaffRecruitDiamondTimes(self.server_id, self.char_id).record(value=recruit_times)

        if diamond_single_free:
            converted_tp = 3
        else:
            converted_tp = tp

        config = ConfigStaffRecruit.get(converted_tp)

        # times 3 和 2 还是公用的
        current_times = self.get_times(tp) + 1

        # point 是分开计的
        result = RecruitResult(self.get_point(converted_tp))

        for i in range(current_times, current_times + recruit_times):
            res = config.recruit(result.point, i)
            result.add(res)

        self.doc['point'][str(converted_tp)] = result.point

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
        ValueLogStaffRecruitScore(self.server_id, self.char_id).record(sub_id=tp, value=result.add_score)

        MongoStaffRecruit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'point.{0}'.format(converted_tp): result.point,
                'score': self.doc['score']
            }}
        )

        rc = ResourceClassification.classify(result.items)
        rc.add(self.server_id, self.char_id, message="StaffRecruit.recruit:{0},{1}".format(tp, mode))

        if tp == RECRUIT_GOLD:
            recruit_staff_gold_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
                times=recruit_times,
                staffs=rc.staff
            )
        else:
            recruit_staff_diamond_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
                times=recruit_times,
                staffs=rc.staff
            )

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
            resource_classify.remove(self.server_id, self.char_id, message="StaffRecruit.recruit:1,1")

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

        cost = [(money_text_to_item_id('gold'), config.cost_value_10)]

        resource_classify = ResourceClassification.classify(cost)
        resource_classify.check_exist(self.server_id, self.char_id)
        resource_classify.remove(self.server_id, self.char_id, message="StaffRecruit.recruit:1,2")

        return 10

    def _recruit_tp_2_mode_1(self):
        # 钻石单抽
        config = ConfigStaffRecruit.get(2)

        cd_seconds = self.get_cd_seconds(2)
        if cd_seconds:
            cost = [(money_text_to_item_id('diamond'), config.cost_value_1)]

            resource_classify = ResourceClassification.classify(cost)
            resource_classify.check_exist(self.server_id, self.char_id)
            resource_classify.remove(self.server_id, self.char_id, message="StaffRecruit.recruit:2,1")
        else:
            self.doc['recruit_at']['2'] = arrow.utcnow().timestamp

            MongoStaffRecruit.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'recruit_at.2': self.doc['recruit_at']['2']
                }}
            )

        return 1, not bool(cd_seconds)

    def _recruit_tp_2_mode_2(self):
        # 钻石十连抽
        config = ConfigStaffRecruit.get(2)

        cost = [(money_text_to_item_id('diamond'), config.cost_value_10)]

        resource_classify = ResourceClassification.classify(cost)
        resource_classify.check_exist(self.server_id, self.char_id)
        resource_classify.remove(self.server_id, self.char_id, message="StaffRecruit.recruit:2,2")

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
MIN_STAR_EXP = 1
MAX_STAR_EXP = 3
AVG_STAR_EXP = 3.2


class Staff(AbstractStaff):
    __slots__ = ['config_inspire_level_addition', 'config_inspire_step_addition']

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
        self.equip_special = data.get('equip_special', '')

        self.config_inspire_level_addition = None
        self.config_inspire_step_addition = None

        self.after_init()

    def reset(self):
        # 重置到初始状态
        self.level = 1
        self.step = 0
        self.star = 0
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
        max_level = min(ConfigStaffLevelNew.MAX_LEVEL, get_club_property(self.server_id, self.char_id, 'level') * 2)
        if self.level >= max_level:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_ALREADY_MAX_LEVEL"))

        target_level = self.level + up_level
        if target_level > max_level:
            target_level = max_level

        old_level = self.level
        while self.level < target_level:
            config = ConfigStaffLevelNew.get(self.level)
            up_need_exp = config.exp - self.level_exp

            if exp_pool < up_need_exp:
                self.level_exp += exp_pool
                exp_pool = 0
                break

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

        staff_level_up_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            staff_id=self.id,
            staff_oid=self.oid,
            new_level=self.level
        )

        return exp_pool, self.level - old_level

    def step_up(self):
        if self.step >= self.config.max_step:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_ALREADY_MAX_STEP"))

        if self.level < self.config.steps[self.step].level_limit:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_LEVEL_NOT_ENOUGH"))

        using_items = self.config.steps[self.step].update_item_need
        resource_classified = ResourceClassification.classify(using_items)
        resource_classified.check_exist(self.server_id, self.char_id)
        resource_classified.remove(self.server_id, self.char_id, message="Staff.step_up:{0}".format(self.oid))

        self.step += 1
        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'staffs.{0}.step'.format(self.id): self.step
            }}
        )

        # NOTE 升阶可能会导致 天赋技能 改变
        # 不仅会影响自己，可能（如果在阵型中）也会影响到其他选手
        # 所以这里不自己 calculate， 而是先让 club 重新 load staffs

        staff_step_up_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            staff_id=self.id,
            staff_oid=self.oid,
            new_step=self.step
        )

    def star_up(self, single):
        # single = True,  只升级一次
        # single = False, 尽量升到下一星级
        if self.star >= ConfigStaffStar.MAX_STAR:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_ALREADY_MAX_STAR"))

        old_star = self.star

        def _make_single_up():
            star_config = ConfigStaffStar.get(self.star)
            using_items = [(star_config.need_item_id, star_config.need_item_amount)]

            resource_classified = ResourceClassification.classify(using_items)
            resource_classified.check_exist(self.server_id, self.char_id)
            resource_classified.remove(self.server_id, self.char_id, message="Staff.star_up:{0}".format(self.oid))

            if random.randint(1, 100) <= 20:
                _exp = 6
                is_crit = True
            else:
                _exp = random.randint(1, 3)
                is_crit = False

            exp = self.star_exp + _exp

            while True:
                if self.star == ConfigStaffStar.MAX_STAR:
                    if exp >= ConfigStaffStar.get(self.star).exp:
                        exp = ConfigStaffStar.get(self.star).exp - 1

                    break

                if exp < ConfigStaffStar.get(self.star).exp:
                    break

                exp -= ConfigStaffStar.get(self.star).exp
                self.star += 1

            self.star_exp = exp

            return is_crit, _exp, star_config.need_item_id, star_config.need_item_amount

        if single:
            crit, inc_exp, cost_item_id, cost_item_amount = _make_single_up()
        else:
            crit = False
            inc_exp = 0
            cost_item_id = 0
            cost_item_amount = 0

            while self.star == old_star:
                try:
                    _crit, _inc_exp, _cost_id, _cost_amount = _make_single_up()
                except GameException as e:
                    if not inc_exp:
                        # 说明一次都没成功
                        raise e
                    else:
                        break

                if _crit:
                    crit = _crit

                inc_exp += _inc_exp
                cost_item_id = _cost_id
                cost_item_amount += _cost_amount

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'staffs.{0}.star'.format(self.id): self.star,
                'staffs.{0}.star_exp'.format(self.id): self.star_exp
            }}
        )

        if self.star != old_star:
            self.calculate()

        self.make_cache()

        star_changed = self.star > old_star
        if star_changed:
            staff_star_up_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
                staff_id=self.id,
                staff_oid=self.oid,
                new_star=self.star
            )

        return star_changed, crit, inc_exp, cost_item_id, cost_item_amount

    def equipment_change(self, bag_slot_id, tp):
        # 会影响的其他staff_id
        other_staff_id = ""

        if not bag_slot_id:
            # 卸下
            bag_slot_id = ""
        else:
            # 更换
            bag = Bag(self.server_id, self.char_id)
            slot = bag.get_slot(bag_slot_id)

            item_id = slot['item_id']
            if get_item_type(item_id) != TYPE_EQUIPMENT:
                raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

            equip_config = ConfigEquipmentNew.get(item_id)
            if equip_config.tp != tp:
                raise GameException(ConfigErrorMessage.get_error_id("EQUIPMENT_TYPE_NOT_MATCH"))

            other_staff_id = StaffManger(self.server_id, self.char_id).find_staff_id_by_equipment_slot_id(bag_slot_id)

        if tp == EQUIP_MOUSE:
            key = 'equip_mouse'
        elif tp == EQUIP_KEYBOARD:
            key = 'equip_keyboard'
        elif tp == EQUIP_MONITOR:
            key = 'equip_monitor'
        elif tp == EQUIP_DECORATION:
            key = 'equip_decoration'
        elif tp == EQUIP_SPECIAL:
            key = 'equip_special'
        else:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        setattr(self, key, bag_slot_id)
        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'staffs.{0}.{1}'.format(self.id, key): bag_slot_id
            }}
        )

        self.calculate()
        self.make_cache()

        return other_staff_id

    def add_equipment_property_for_staff(self):
        bag = Bag(self.server_id, self.char_id)

        levels = []
        qualities = []

        # 装备本身属性
        for slot_id in [self.equip_keyboard, self.equip_monitor, self.equip_mouse, self.equip_decoration,
                        self.equip_special]:
            if not slot_id:
                continue

            data = bag.get_slot(slot_id)
            config = ConfigItemNew.get(data['item_id'])

            equip = Equipment.load_from_slot_data(data)

            self.attack += equip.staff_attack
            self.defense += equip.staff_defense
            self.manage += equip.staff_manage
            self.operation += equip.staff_operation

            self.attack_percent += equip.get_property_value(PROPERTY_STAFF_ATTACK_PERCENT)
            self.defense_percent += equip.get_property_value(PROPERTY_STAFF_DEFENSE_PERCENT)
            self.manage_percent += equip.get_property_value(PROPERTY_STAFF_MANAGE_PERCENT)
            self.operation_percent += equip.get_property_value(PROPERTY_STAFF_OPERATION_PERCENT)

            if slot_id not in [self.equip_decoration, self.equip_special]:
                # 装备加成不算 饰品，神器
                levels.append(data['level'])
                qualities.append(config.quality)

        # 装备加成
        if len(levels) == 3:
            equip_level_addition = ConfigStaffEquipmentAddition.get_by_level(min(levels))
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

    def add_equipment_property_for_unit(self):
        if not self.equip_special:
            return

        # NOTE !!!
        unit = self.unit
        if not unit:
            return

        bag = Bag(self.server_id, self.char_id)
        data = bag.get_slot(self.equip_special)

        equip = Equipment.load_from_slot_data(data)

        unit.hp_percent += equip.get_property_value(PROPERTY_UNIT_HP_PERCENT)
        unit.attack_percent += equip.get_property_value(PROPERTY_UNIT_ATTACK_PERCENT)
        unit.defense_percent += equip.get_property_value(PROPERTY_UNIT_DEFENSE_PERCENT)
        unit.hit_rate += equip.get_property_value(PROPERTY_UNIT_HIT_PERCENT)
        unit.dodge_rate += equip.get_property_value(PROPERTY_UNIT_DODGE_PERCENT)
        unit.crit_rate += equip.get_property_value(PROPERTY_UNIT_CRIT_PERCENT)
        unit.toughness_rate += equip.get_property_value(PROPERTY_UNIT_TOUGHNESS_PERCENT)
        unit.crit_multiple += equip.get_property_value(PROPERTY_UNIT_CRIT_MULTIPLE)

        unit.hurt_addition_to_terran += equip.get_property_value(PROPERTY_UNIT_HURT_ADDIITON_TO_TERRAN)
        unit.hurt_addition_to_protoss += equip.get_property_value(PROPERTY_UNIT_HURT_ADDIITON_TO_PROTOSS)
        unit.hurt_addition_to_zerg += equip.get_property_value(PROPERTY_UNIT_HURT_ADDIITON_TO_ZERG)

        unit.hurt_addition_by_terran += equip.get_property_value(PROPERTY_UNIT_HURT_ADDIITON_BY_TERRAN)
        unit.hurt_addition_by_protoss += equip.get_property_value(PROPERTY_UNIT_HURT_ADDIITON_BY_PROTOSS)
        unit.hurt_addition_by_zerg += equip.get_property_value(PROPERTY_UNIT_HURT_ADDIITON_BY_ZERG)

        unit.final_hurt_addition += equip.get_property_value(PROPERTY_UNIT_FINAL_HURT_ADDITION)
        unit.final_hurt_reduce += equip.get_property_value(PROPERTY_UNIT_FINAL_HURT_REDUCE)

    def add_inspire_addition_for_staff(self):
        addition = getattr(self, 'config_inspire_level_addition', None)
        """:type: config.qianban.InspireLevelAddition | None"""
        if not addition:
            return

        self.attack += addition.attack
        self.attack_percent += addition.attack_percent
        self.defense += addition.defense
        self.defense_percent += addition.defense_percent
        self.manage += addition.manage
        self.manage_percent += addition.manage_percent
        self.operation += addition.operation
        self.operation_percent += addition.operation_percent

    def add_inspire_addition_for_unit(self):
        addition = getattr(self, 'config_inspire_step_addition', None)
        """:type: config.qianban.InspireStepAddition | None"""

        if not addition:
            return

        unit = self.unit
        if not unit:
            return

        unit.hp_percent += addition.hp_percent
        unit.attack_percent += addition.attack_percent
        unit.defense_percent += addition.defense_percent
        unit.hit_rate += addition.hit_rate
        unit.dodge_rate += addition.dodge_rate
        unit.crit_rate += addition.crit_rate
        unit.toughness_rate += addition.toughness_rate
        unit.crit_multiple += addition.crit_multiple

        unit.hurt_addition_to_terran += addition.hurt_addition_to_terran
        unit.hurt_addition_to_protoss += addition.hurt_addition_to_protoss
        unit.hurt_addition_to_zerg += addition.hurt_addition_to_zerg

        unit.hurt_addition_by_terran += addition.hurt_addition_by_terran
        unit.hurt_addition_by_protoss += addition.hurt_addition_by_protoss
        unit.hurt_addition_by_zerg += addition.hurt_addition_by_zerg

    def get_cost_items(self, percent=100):
        # 得到一路升级过来所消耗的物品
        items = {}

        def _add_to_items(__id, __amount):
            if __id in items:
                items[__id] += __amount
            else:
                items[__id] = __amount

        exp = self.level_exp
        for i in range(self.level - 1, 0, -1):
            exp += ConfigStaffLevelNew.get(i).exp

        exp = exp * percent / 100.0

        _add_to_items(STAFF_EXP_POOL_ID, int(exp))

        # 升星道具
        for i in range(self.star - 1, -1, -1):
            config = ConfigStaffStar.get(i)
            amount = config.exp * percent / 100.0 / AVG_STAR_EXP * config.need_item_amount
            if amount:
                _add_to_items(config.need_item_id, amount)

        # 升阶道具
        for i in range(self.step - 1, -1, -1):
            config = self.config.steps[i]
            for _id, _amount in config.update_item_need:
                _amount = _amount * percent / 100.0
                _add_to_items(_id, _amount)

        results = []
        for k, v in items.iteritems():
            v = int(round(v))
            if v:
                results.append((k, v))

        return results


class StaffManger(object):
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoStaff.exist(self.server_id, self.char_id):
            doc = MongoStaff.document()
            doc['_id'] = self.char_id
            MongoStaff.db(server_id).insert_one(doc)

    def add_exp_pool(self, exp):
        doc = MongoStaff.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'exp_pool': 1}
        )

        new_exp = doc.get('exp_pool', 0) + exp
        if new_exp > MAX_INT:
            new_exp = MAX_INT

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'exp_pool': new_exp
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

    def after_staffs_change_for_trig_signal(self):
        task_condition_trig_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            condition_name='core.staff.StaffManger'
        )

    def get_staffs_amount_by_level(self, level, method='gte'):
        staffs = self.get_staffs_data()
        amount = 0
        for k, v in staffs.iteritems():
            if method == 'gte':
                if v['level'] >= level:
                    amount += 1
            else:
                if v['level'] == level:
                    amount += 1

        return amount

    def get_staffs_amount_by_step(self, step, method='gte'):
        staffs = self.get_staffs_data()
        amount = 0
        for k, v in staffs.iteritems():
            if method == 'gte':
                if v['step'] >= step:
                    amount += 1
            else:
                if v['step'] == step:
                    amount += 1

        return amount

    def get_staffs_amount_by_star(self, star, method='gte'):
        staffs = self.get_staffs_data()
        amount = 0
        for k, v in staffs.iteritems():
            if method == 'gte':
                if v['star'] / 10 >= star:
                    amount += 1
            else:
                if v['star'] / 10 == star:
                    amount += 1

        return amount

    def find_staff_id_with_equip(self, bag_slot_id):
        keys = ['equip_mouse', 'equip_keyboard', 'equip_monitor', 'equip_decoration', 'equip_special']

        staffs = self.get_staffs_data()
        for k, v in staffs.iteritems():
            for key in keys:
                if v.get(key, "") == bag_slot_id:
                    return k

        return None

    def get_all_staff_object(self):
        """

        :rtype: dict[str, Staff]
        """
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, {'staffs': 1})
        return {k: self.get_staff_object(k) for k, _ in doc['staffs'].iteritems()}

    def get_staff_object(self, _id):
        """

        :param _id:
        :rtype : Staff
        """
        from core.club import Club

        obj = Staff.get(_id)
        if obj:
            return obj

        Club(self.server_id, self.char_id, load_staffs=False).force_load_staffs()
        obj = Staff.get(_id)
        if obj:
            return obj

        raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

    def has_staff(self, ids):
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
        packed_originals = {}
        for _oid, _amount in originals:
            if _oid not in packed_originals:
                packed_originals[_oid] = _amount
            else:
                packed_originals[_oid] += _amount

        staffs = self.get_all_staff_object().values()
        result = {}
        """:type: dict[int, list]"""

        for _oid, _amount in originals:
            if _oid not in result:
                result[_oid] = []

            for s in staffs:
                if s.oid == _oid and s.is_initial_state() and \
                        checker.staff_not_working(self.server_id, self.char_id, s.id, raise_exception=False):

                    result[_oid].append(s.id)

            if len(result[_oid]) < _amount:
                # TODO replace the error code
                raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

            result[_oid] = result[_oid][:_amount]

        return result

    def add(self, staff_original_id, send_notify=True, trig_signal=True):
        if not ConfigStaffNew.get(staff_original_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        unique_id = make_string_id()
        doc = MongoStaff.document_staff()
        doc['oid'] = staff_original_id

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
            staffs_info=[(staff_original_id, unique_id), ],
            force_load_staffs=send_notify,
        )

        if trig_signal:
            self.after_staffs_change_for_trig_signal()
        return unique_id

    def batch_add(self, staffs):
        # [(oid, amount), ...]

        updater = {}
        unique_id_list = []

        info = []

        for oid, amount in staffs:
            if not ConfigStaffNew.get(oid):
                raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

            for i in range(amount):
                unique_id = make_string_id()
                doc = MongoStaff.document_staff()
                doc['oid'] = oid

                unique_id_list.append(unique_id)
                updater['staffs.{0}'.format(unique_id)] = doc
                info.append((oid, unique_id))

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_notify(ids=unique_id_list)

        staff_new_add_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            staffs_info=info,
            force_load_staffs=True,
        )

        self.after_staffs_change_for_trig_signal()

    def remove(self, staff_id):
        if isinstance(staff_id, (list, tuple)):
            staff_ids = staff_id
        else:
            staff_ids = [staff_id]

        updater = {'staffs.{0}'.format(i): 1 for i in staff_ids}
        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$unset': updater}
        )

        for i in staff_ids:
            Staff.clean_cache(i)

        notify = StaffRemoveNotify()
        notify.ids.extend(staff_ids)
        MessagePipe(self.char_id).put(msg=notify)
        self.after_staffs_change_for_trig_signal()

    def internal_remove_by_oid(self, originals):
        # 内部删除
        # 现在只有 通过 ResourceClassification 的 remove
        result = self.check_original_staff_is_initial_state(originals)
        ids = []
        for _, v in result.iteritems():
            ids.extend(v)

        self.remove(ids)

    def find_staff_id_by_equipment_slot_id(self, slot_id):
        # type: (str) -> str
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
                            v['equip_decoration'] == slot_id or \
                            v.get('equip_special', '') == slot_id:
                return k

        return ""

    def after_staff_change(self):
        from core.club import Club
        Club(self.server_id, self.char_id).send_notify()

    def equipment_change(self, staff_id, slot_id, tp):
        from core.formation import Formation

        if tp not in [EQUIP_MOUSE, EQUIP_KEYBOARD, EQUIP_MONITOR, EQUIP_DECORATION, EQUIP_SPECIAL]:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        staff = self.get_staff_object(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        other_staff_id = staff.equipment_change(slot_id, tp)
        if other_staff_id:
            # 把装备从 这个 staff 上撤下
            self.get_staff_object(other_staff_id).equipment_change("", tp)

        changed = [staff_id]
        if other_staff_id:
            changed.append(other_staff_id)

        self.send_notify(ids=changed)

        in_formation_staff_ids = Formation(self.server_id, self.char_id).in_formation_staffs().keys()
        if staff.id in in_formation_staff_ids or other_staff_id in in_formation_staff_ids:
            self.after_staff_change()

            task_condition_trig_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
                condition_name='core.formation.Formation'
            )

    def level_up(self, staff_id, up_level):
        from core.formation import Formation
        staff = self.get_staff_object(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        doc = MongoStaff.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'exp_pool': 1}
        )

        exp_pool = doc.get('exp_pool', 0)
        remained_exp_pool, _level_up_amount = staff.level_up(exp_pool, up_level)

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'exp_pool': remained_exp_pool
            }}
        )

        self.send_notify(ids=[staff_id])

        if _level_up_amount:
            ValueLogStaffLevelUpTimes(self.server_id, self.char_id).record(value=_level_up_amount)

            in_formation_staff_ids = Formation(self.server_id, self.char_id).in_formation_staffs().keys()
            if staff.id in in_formation_staff_ids:
                self.after_staff_change()

            self.after_staffs_change_for_trig_signal()

    def step_up(self, staff_id):
        from core.club import Club
        from core.formation import Formation
        staff = self.get_staff_object(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        staff.step_up()
        in_formation_staff_ids = Formation(self.server_id, self.char_id).in_formation_staffs().keys()
        if staff.id in in_formation_staff_ids:
            Club(self.server_id, self.char_id, load_staffs=False).force_load_staffs(send_notify=True)
        else:
            staff.calculate()
            staff.make_cache()
            self.send_notify(ids=[staff_id])

        self.after_staffs_change_for_trig_signal()

    def star_up(self, staff_id, single):
        from core.formation import Formation
        staff = self.get_staff_object(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        _star_up, crit, inc_exp, cost_item_id, cost_item_amount = staff.star_up(single)
        ValueLogStaffStarUpTimes(self.server_id, self.char_id).record()
        self.send_notify(ids=[staff_id])

        in_formation_staff_ids = Formation(self.server_id, self.char_id).in_formation_staffs().keys()
        if _star_up and staff.id in in_formation_staff_ids:
            self.after_staff_change()
            self.after_staffs_change_for_trig_signal()

        return crit, inc_exp, cost_item_id, cost_item_amount

    def _destroy_check(self, staff_id):
        from core.territory import Territory
        checker.staff_not_working(self.server_id, self.char_id, staff_id)

        if Territory(self.server_id, self.char_id).is_staff_training_check_by_unique_id(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_CANNOT_DESTROY_IN_TERRITORY"))

    def destroy(self, staff_id, tp):
        from core.club import Club
        from core.formation import Formation

        self._destroy_check(staff_id)

        staff = self.get_staff_object(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        if tp == 0:
            # 普通分解
            items = staff.get_cost_items(70)
            crystal = ConfigStaffNew.get(staff.oid).crystal
            items.append((money_text_to_item_id('crystal'), crystal))
        else:
            if staff.is_initial_state():
                raise GameException(ConfigErrorMessage.get_error_id("STAFF_CANNOT_DESTROY_INITIAL_STATE"))

            # TODO diamond count
            resource_classified = ResourceClassification.classify([(money_text_to_item_id('diamond'), 50)])
            resource_classified.check_exist(self.server_id, self.char_id)
            resource_classified.remove(self.server_id, self.char_id,
                                       message="StaffManger.destroy:{0},{1}".format(staff.oid, tp))

            items = staff.get_cost_items(100)

        resource_classified = ResourceClassification.classify(items)
        resource_classified.add(self.server_id, self.char_id,
                                message="StaffManger.destroy:{0},{1}".format(staff.oid, tp))

        if tp == 0:
            self.remove(staff_id)
        else:
            staff.reset()
            in_formation_staff_ids = Formation(self.server_id, self.char_id).in_formation_staffs().keys()
            if staff.id in in_formation_staff_ids:
                Club(self.server_id, self.char_id, load_staffs=False).force_load_staffs(send_notify=True)
            else:
                staff.calculate()
                staff.make_cache()
                self.send_notify(ids=[staff_id])

        self.after_staffs_change_for_trig_signal()
        return resource_classified

    def batch_destroy(self, staff_ids):
        total_items = {}

        for sid in staff_ids:
            self._destroy_check(sid)

            staff = self.get_staff_object(sid)
            if not staff:
                raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

            _items = staff.get_cost_items(70)
            _crystal = ConfigStaffNew.get(staff.oid).crystal
            _items.append((money_text_to_item_id('crystal'), _crystal))

            for _id, _amount in _items:
                if _id in total_items:
                    total_items[_id] += _amount
                else:
                    total_items[_id] = _amount

        rc = ResourceClassification.classify(total_items.items())
        rc.add(self.server_id, self.char_id, message="StaffManger.batch_destroy")

        self.remove(staff_ids)
        self.after_staffs_change_for_trig_signal()
        return rc

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
