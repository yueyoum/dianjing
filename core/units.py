
from config.unit import ConfigUnitNew, ConfigUnitUnLock
from config.errormsg import ConfigErrorMessage

from core.abstract import AbstractUnit
from core.mongo import MongoUnit
from core.club import Club
from core.resource import ResourceClassification

from dianjing.exception import GameException

from utils.functional import make_string_id
from utils.message import MessagePipe

from protomsg.unit_pb2 import UnitNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE


class Unit(AbstractUnit):
    __slots__ = ['conf_unit', 'conf_step', 'conf_level']

    def __init__(self, uid, data):
        super(Unit, self).__init__()
        self.uid = uid
        self.oid = data['oid']
        self.step = data['step']
        self.level = data['level']

        self.conf_unit = ConfigUnitNew.get(self.oid)
        self.conf_step = self.conf_unit.steps.get(self.step)
        self.conf_level = self.conf_unit.levels.get(self.level)

        self.tp = self.conf_unit.tp
        self.race = self.conf_unit.race
        self.attack_tp = self.conf_unit.attack_tp
        self.defense_tp = self.conf_unit.defense_tp
        self.skill_1 = self.conf_unit.skill_1
        self.skill_2 = self.conf_unit.skill_2

        self.calculate()

    def calculate(self):
        self.hp_percent = self.conf_step.hp_percent
        self.hp = (self.conf_unit.hp_max_base + self.conf_level.hp) * (1 + self.hp_percent)

        self.attack_percent = self.conf_step.attack_percent
        self.attack = (self.conf_unit.attack_base + self.conf_level.attack) * (1 + self.attack_percent)

        self.defense_percent = self.conf_step.defense_percent
        self.defense = (self.conf_unit.defense_base + self.conf_level.defense) * (1 + self.defense_percent)

        self.attack_speed = self.conf_unit.attack_speed_base
        self.attack_distance = self.conf_unit.attack_range_base
        self.move_speed = self.conf_unit.move_speed_base
        self.hit_rate = self.conf_step.hit_rate + self.conf_unit.hit_rate
        self.dodge_rate = self.conf_unit.dodge_rate + self.conf_step.dodge_rate
        self.crit_rate = self.conf_unit.crit_rate + self.conf_step.crit_rate
        self.crit_multi = self.conf_unit.crit_multiple + self.conf_step.crit_multiple
        self.crit_anti_rate = self.conf_unit.toughness_rate + self.conf_step.toughness_rate
        self.append_attack_terran = self.conf_unit.hurt_addition_to_terran + self.conf_step.hurt_addition_to_terran
        self.append_attack_protoss = self.conf_unit.hurt_addition_to_protoss + self.conf_step.hurt_addition_to_protoss
        self.append_attack_zerg = self.conf_unit.hurt_addition_to_zerg + self.conf_step.hurt_addition_to_zerg
        self.append_attacked_by_terran = self.conf_unit.hurt_addition_by_terran + self.conf_step.hurt_addition_by_terran
        self.append_attacked_by_protoss = self.conf_unit.hurt_addition_by_protoss + self.conf_step.hurt_addition_by_protoss
        self.append_attacked_by_zerg = self.conf_unit.hurt_addition_by_zerg + self.conf_step.hurt_addition_by_zerg
        self.final_hurt_append = self.conf_unit.final_hurt_addition
        self.final_hurt_reduce = self.conf_unit.final_hurt_reduce


def get_init_units():
    units = []
    units_conf = ConfigUnitUnLock.INSTANCES
    for k, v in units_conf.items():
        if v.need_club_level == 0 and not v.need_unit_level:
            units.append(k)

    return units


class UnitManager(object):
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoUnit.exist(self.server_id, self.char_id):
            unit_ids = get_init_units()

            for k in unit_ids:
                self.unlock(k)

    def unlock(self, oid):
        unlock_conf = ConfigUnitUnLock.get(oid)
        club_lv = Club(self.server_id, self.char_id).level
        if club_lv < unlock_conf.need_club_level:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        # TODO: unlock unit lv check
        # for unlock_conf.need_unit_level.

        unit = MongoUnit.UNIT_DOCUMENT.copy()
        unit['oid'] = unlock_conf.id
        uid = make_string_id()

        MongoUnit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'units.{0}'.format(uid): unit}},
            upsert=True,
        )

    def get_unit(self, uid):
        unit = MongoUnit.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'units.{0}'.format(uid): 1}
        )

        return unit['units'].get(uid, {})

    def item_check(self, using_items):
        resource_classified = ResourceClassification.classify(using_items)
        resource_classified.check_exist(self.server_id, self.char_id)
        resource_classified.remove(self.server_id, self.char_id)

    def level_up(self, uid):
        unit_data = self.get_unit(uid)
        if not unit_data:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        unit_conf = ConfigUnitNew.get(unit_data['oid'])
        if unit_data['level'] >= unit_conf.max_level:
            raise GameException(ConfigErrorMessage.get_error_id("UNIT_REACH_MAX_LEVEL"))

        level_conf = unit_conf.levels.get(unit_data['level'])
        using_items = [(i, j) for i, j in level_conf.update_item_need]
        self.item_check(using_items)

        MongoUnit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {'units.{0}.level': 1}}
        )

        self.send_notify([uid])
        return 0

    def step_up(self, uid):
        unit_data = self.get_unit(uid)
        if not unit_data:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        unit_conf = ConfigUnitNew.get(unit_data['oid'])
        if unit_data['step'] >= unit_conf.max_step:
            raise GameException(ConfigErrorMessage.get_error_id("UNIT_REACH_MAX_STEP"))

        step_conf = unit_conf.steps.get(unit_data['step'])
        if unit_data['level'] < step_conf.level_limit:
            raise GameException(ConfigErrorMessage.get_error_id("UNIT_LEVEL_NOT_ENOUGH"))

        using_items = [(i, k) for i, k in step_conf.update_item_need]
        self.item_check(using_items)

        MongoUnit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {'units.{0}.step': 1}}
        )

        self.send_notify([uid])
        return 0

    def send_notify(self, uid=None):
        if not uid:
            act = ACT_INIT
            projection = {'units': 1}
        else:
            act = ACT_UPDATE
            projection = {'units.{0}'.format(i): 1 for i in uid}

        data = MongoUnit.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

        notify = UnitNotify()
        notify.act = act
        for k, v in data['units'].iteritems():
            unit_info = notify.units.add()
            if not v:
                continue

            unit = Unit(k, v)
            unit_info.id = unit.uid
            unit_info.oid = unit.oid
            unit_info.level = unit.level
            unit_info.step = unit.step
            unit_info.hp = unit.hp
            unit_info.attack = unit.attack
            unit_info.defense = unit.defense

        MessagePipe(self.char_id).put(msg=notify)
