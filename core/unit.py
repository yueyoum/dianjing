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

from utils.functional import make_string_id
from utils.message import MessagePipe

from config import ConfigErrorMessage, ConfigUnitNew, ConfigUnitUnLock

from protomsg.unit_pb2 import UnitNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE


class Unit(AbstractUnit):
    __slots__ = ['conf_unit', 'server_id', 'char_id']

    def __init__(self, server_id, char_id, uid, data):
        super(Unit, self).__init__()
        self.server_id = server_id
        self.char_id = char_id
        self.id = uid
        self.oid = data['oid']
        self.step = data['step']
        self.level = data['level']

        self.conf_unit = ConfigUnitNew.get(self.oid)

        self.tp = self.conf_unit.tp
        self.race = self.conf_unit.race
        self.attack_tp = self.conf_unit.attack_tp
        self.defense_tp = self.conf_unit.defense_tp
        self.skill_1 = self.conf_unit.skill_1
        self.skill_2 = self.conf_unit.skill_2

        # 分成两阶段计算是因为：
        # 1, 改变了等级，等阶，直接调用以下这两个方法
        # 2, 外部效果对兵种有加成，就先把加成加上去，然后再调用第二步计算
        self.pre_calculate_property()
        self.calculate_property()

    def pre_calculate_property(self):
        conf_step = self.conf_unit.steps[self.step]
        
        self.hp_percent = conf_step.hp_percent
        self.attack_percent = conf_step.attack_percent
        self.defense_percent = conf_step.defense_percent

        self.attack_speed = self.conf_unit.attack_speed_base
        self.attack_distance = self.conf_unit.attack_range_base
        self.move_speed = self.conf_unit.move_speed_base
        self.hit_rate = conf_step.hit_rate + self.conf_unit.hit_rate
        self.dodge_rate = self.conf_unit.dodge_rate + conf_step.dodge_rate
        self.crit_rate = self.conf_unit.crit_rate + conf_step.crit_rate
        self.crit_multi = self.conf_unit.crit_multiple + conf_step.crit_multiple
        self.crit_anti_rate = self.conf_unit.toughness_rate + conf_step.toughness_rate
        self.append_attack_terran = conf_step.hurt_addition_to_terran + conf_step.hurt_addition_to_terran
        self.append_attack_protoss = conf_step.hurt_addition_to_protoss + conf_step.hurt_addition_to_protoss
        self.append_attack_zerg = conf_step.hurt_addition_to_zerg + conf_step.hurt_addition_to_zerg
        self.append_attacked_by_terran = conf_step.hurt_addition_by_terran + conf_step.hurt_addition_by_terran
        self.append_attacked_by_protoss = conf_step.hurt_addition_by_protoss + conf_step.hurt_addition_by_protoss
        self.append_attacked_by_zerg = conf_step.hurt_addition_by_zerg + conf_step.hurt_addition_by_zerg
        self.final_hurt_append = self.conf_unit.final_hurt_addition
        self.final_hurt_reduce = self.conf_unit.final_hurt_reduce

    def calculate_property(self):
        conf_level = self.conf_unit.levels[self.level]
        self.hp = (self.conf_unit.hp_max_base + conf_level.hp) * (1 + self.hp_percent)
        self.attack = (self.conf_unit.attack_base + conf_level.attack) * (1 + self.attack_percent)
        self.defense = (self.conf_unit.defense_base + conf_level.defense) * (1 + self.defense_percent)


    def level_up(self):
        if self.level >= self.conf_unit.max_level:
            raise GameException(ConfigErrorMessage.get_error_id("UNIT_REACH_MAX_LEVEL"))

        using_items = self.conf_unit.levels[self.level].update_item_need
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

        self.pre_calculate_property()
        self.calculate_property()
        self.send_notify()

    def step_up(self):
        if self.step >= self.conf_unit.max_step:
            raise GameException(ConfigErrorMessage.get_error_id("UNIT_REACH_MAX_STEP"))

        if self.level < self.conf_unit.steps[self.step].level_limit:
            raise GameException(ConfigErrorMessage.get_error_id("UNIT_LEVEL_NOT_ENOUGH"))

        using_items = self.conf_unit.steps[self.step].update_item_need
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

        self.pre_calculate_property()
        self.calculate_property()
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

            for oid in init_ids:
                unique_id = make_string_id()

                unit_doc = MongoUnit.document_unit()
                unit_doc['oid'] = oid

                doc['units'][unique_id] = unit_doc

            doc['unlocked'] = init_ids
            MongoUnit.db(self.server_id).insert_one(doc)


    def unlock_club_level_up_listener(self, club_level):
        pass

    def unlock_unit_level_up_listener(self, club_level):
        pass

    def _unlock(self, oid):
        doc = MongoUnit.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'unlocked': 1}
        )

        if oid in doc['unlocked']:
            return

        unlock_conf = ConfigUnitUnLock.get(oid)
        club_lv = Club(self.server_id, self.char_id).level
        if club_lv < unlock_conf.need_club_level:
            # TODO error message
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        # TODO: unlock unit lv check
        # for unlock_conf.need_unit_level.

        unit = MongoUnit.document_unit()
        unit['oid'] = oid
        unique_id = make_string_id()

        MongoUnit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'units.{0}'.format(unique_id): unit}},
            upsert=True,
        )

        self.send_notify(uids=[unique_id])

    def get_unit_object(self, unique_id):
        # type: (str) -> Unit|None
        doc = MongoUnit.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'units.{0}'.format(unique_id): 1}
        )

        data = doc['units'].get(unique_id, None)
        if not data:
            return None

        return Unit(self.server_id, self.char_id, unique_id, data)

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
            unit = Unit(self.server_id, self.char_id, k, v)
            notify_unit.MergeFrom(unit.make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)
