
from config.unit import ConfigUnitNew, ConfigUnitUnLock
from config.errormsg import ConfigErrorMessage

from core.abstract import AbstractUnit
from core.mongo import MongoUnit
from core.club import Club

from dianjing.exception import GameException

from utils.functional import make_string_id
from utils.message import MessagePipe

from protomsg.unit_pb2 import UnitNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE


class Unit(AbstractUnit):
    def __init__(self, uid, data):
        super(Unit, self).__init__()
        self.uid = uid
        self.oid = data['oid']
        self.step = data['step']
        self.level = data['level']

        self.conf_unit = ConfigUnitNew.get(self.oid)\

        self.calculate()

    def calculate(self):
        self.hp = self.conf_unit.hp_max_base
        self.hp_percent = 0.0
        self.attack = 0
        self.attack_percent = 0.0
        self.defense = 0
        self.defense_percent = 0.0
        self.attack_speed = 0
        self.attack_speed_percent = 0.0
        self.attack_distance = 0
        self.attack_distance_percent = 0.0
        self.move_speed = 0
        self.move_speed_percent = 0.0
        self.hit_rate = 0.0
        self.dodge_rate = 0.0
        self.crit_rate = 0.0
        self.crit_multi = 0.0
        self.crit_anti_rate = 0.0
        self.append_attack_terran = 0.0
        self.append_attack_protoss = 0.0
        self.append_attack_zerg = 0.0
        self.append_attacked_by_terran = 0.0
        self.append_attacked_by_protoss = 0.0
        self.append_attacked_by_zerg = 0.0
        self.final_hurt_append = 0
        self.final_hurt_reduce = 0


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
        unit.oid = unlock_conf.id
        uid = make_string_id()

        MongoUnit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'units.{0}'.format(uid): unit}},
            upsert=True,
        )

    def get_unit(self, uid):
        return MongoUnit.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'units.{0}'.format(uid): 1}
        )

    def level_up(self, uid):
        if not self.get_unit(uid):
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        # check item

        MongoUnit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {'units.{0}.level': 1}}
        )

        self.send_notify(uid)
        return 0

    def step_up(self, uid):
        if not self.get_unit(uid):
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        # check item

        MongoUnit.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {'units.{0}.step': 1}}
        )

        self.send_notify(uid)
        return 0

    def send_notify(self, uid=None):
        if not uid:
            act = ACT_INIT
        else:
            act = ACT_UPDATE

        notify = UnitNotify()
        notify.act = act
        for k in uid:
            unit_info = notify.units.add()
            unit_data = self.get_unit(k)
            if not unit_data:
                continue

            unit = Unit(k, unit_data)

            unit_info.id = unit.uid
            unit_info.oid = unit.oid
            unit_info.level = unit.level
            unit_info.step = unit.step
            unit_info.hp = unit.hp
            unit_info.attack = unit.attack
            unit_info.defense = unit.defense

        MessagePipe(self.char_id).put(msg=notify)
