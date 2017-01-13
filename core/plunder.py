# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       plunder
Date Created:   2016-08-18 14:45
Description:

"""

import random
import arrow

from django.conf import settings

from dianjing.exception import GameException

from core.mongo import (
    MongoCharacter,
    MongoPlunder,
    MongoPlunderFormationWay1,
    MongoPlunderFormationWay2,
    MongoPlunderFormationWay3,

    MongoSpecialEquipment,
)

from core.club import get_club_property, Club
from core.formation import BaseFormation
from core.staff import StaffManger, Staff
from core.cooldown import PlunderSearchCD, PlunderMatchCD
from core.match import ClubMatch
from core.value_log import ValueLogPlunderRevengeTimes, ValueLogPlunderTimes, ValueLogPlunderBuyTimes, \
    ValueLogSpecialEquipmentGenerateTimes
from core.resource import ResourceClassification, STATION_EXP_ID, money_text_to_item_id
from core.bag import Bag, Equipment, PROPERTY_TO_NAME_MAP, SPECIAL_EQUIPMENT_BASE_PROPERTY
from core.vip import VIP

from utils.message import MessagePipe
from utils.functional import make_string_id, get_start_time_of_today

from config import (
    ConfigErrorMessage,
    ConfigBaseStationLevel,
    ConfigPlunderBuyTimesCost,
    ConfigPlunderIncome,
    ConfigEquipmentSpecialGrowingProperty,
    ConfigEquipmentSpecial,
    ConfigEquipmentSpecialScoreToGrowing,
    ConfigEquipmentSpecialGenerate,
    ConfigPlunderNPC,
    ConfigNPCFormation,
    ConfigPlunderDailyReward,

    GlobalConfig,
)

from protomsg.plunder_pb2 import (
    BaseStationNotify,
    PlunderFormationNotify,
    PlunderResultNotify,
    PlunderRevengeNotify,
    PlunderSearchNotify,
    PlunderTimesNotify,

    PlunderFormation as MsgPlunderFormation,

    PLUNDER_TYPE_PLUNDER,
    PLUNDER_TYPE_REVENGE,

    PlunderDailyRewardNotify,

    SpecialEquipmentGenerateNotify,
)

from protomsg.formation_pb2 import FORMATION_SLOT_EMPTY, FORMATION_SLOT_USE
from protomsg.common_pb2 import SPECIAL_EQUIPMENT_GENERATE_NORMAL, SPECIAL_EQUIPMENT_GENERATE_ADVANCE

PLUNDER_ACTIVE_CLUB_LEVEL = 19
REVENGE_MAX_TIMES = 3
PLUNDER_TIMES_INIT_TIMES = 3
PLUNDER_TIMES_RECOVER_LIMIT = 6
PLUNDER_MAX_LOST = 75


class PlunderFormation(BaseFormation):
    __slots__ = ['way_id', 'formation_staffs']
    MONGO_COLLECTION = None

    def __init__(self, server_id, char_id, way_id):
        super(PlunderFormation, self).__init__(server_id, char_id)
        self.way_id = way_id
        self.formation_staffs = []
        """:type: list[core.abstract.AbstractStaff]"""

        self.load_formation_staffs()

    def get_or_create_doc(self):
        doc = self.MONGO_COLLECTION.db(self.server_id).find_one({'_id': self.char_id})
        if not doc:
            # 3个slot直接开好
            slot_doc = self.MONGO_COLLECTION.document_slot()

            doc = self.MONGO_COLLECTION.document()
            doc['_id'] = self.char_id
            doc['position'] = [0] * 30
            doc['slots'] = {
                '1': slot_doc,
                '2': slot_doc,
                '3': slot_doc,
            }

            self.MONGO_COLLECTION.db(self.server_id).insert_one(doc)

        return doc

    def try_unset_staff(self, staff_id):
        in_formation_staffs = self.in_formation_staffs()
        data = in_formation_staffs.get(staff_id, None)
        if not data:
            return False

        slot_id = data['slot_id']
        position = data['position']

        self.doc['slots'][str(slot_id)]['staff_id'] = ''
        self.doc['slots'][str(slot_id)]['unit_id'] = 0
        self.doc['slots'][str(slot_id)]['policy'] = 1

        updater = {
            'slots.{0}.staff_id'.format(slot_id): '',
            'slots.{0}.unit_id'.format(slot_id): 0,
            'slots.{0}.policy'.format(slot_id): 1,
        }

        if position != -1:
            self.doc['position'][position] = 0
            updater['position.{0}'.format(position)] = 0

        self.MONGO_COLLECTION.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        return True

    def set_staff(self, slot_id, staff_id):
        super(PlunderFormation, self).set_staff(slot_id, staff_id)
        self.load_formation_staffs()

    def set_unit(self, slot_id, unit_id):
        super(PlunderFormation, self).set_unit(slot_id, unit_id)
        self.load_formation_staffs()

    def load_formation_staffs(self):
        # NOTE: 这段代码其实是从 Club.force_load_staffs 抄来的
        from core.formation import Formation
        from core.unit import UnitManager
        from core.talent import TalentManager
        from core.collection import Collection
        from core.party import Party
        from core.inspire import Inspire

        self.formation_staffs = []
        """:type: list[core.staff.Staff]"""

        sm = StaffManger(self.server_id, self.char_id)
        fm = Formation(self.server_id, self.char_id)
        um = UnitManager(self.server_id, self.char_id)
        ins = Inspire(self.server_id, self.char_id)

        staffs = sm.get_staffs_data()
        in_formation_staffs = self.in_formation_staffs()

        for k, v in in_formation_staffs.iteritems():
            obj = Staff(self.server_id, self.char_id, k, staffs[k])
            self.formation_staffs.append(obj)

            obj.policy = in_formation_staffs[k]['policy']
            obj.formation_position = in_formation_staffs[k]['position']
            unit_id = in_formation_staffs[k]['unit_id']
            if unit_id:
                obj.set_unit(um.get_unit_object(unit_id))

        club = Club(self.server_id, self.char_id, load_staffs=False)
        club.formation_staffs = self.formation_staffs

        working_staff_oids = self.working_staff_oids()

        for obj in self.formation_staffs:
            obj.check_qianban(working_staff_oids)
            obj.add_self_talent_effect(club)

        talent_effects_1 = TalentManager(self.server_id, self.char_id).get_talent_effects()
        talent_effects_2 = Collection(self.server_id, self.char_id).get_talent_effects()
        talent_effects_3 = fm.get_talent_effects()
        talent_effects_4 = Party(self.server_id, self.char_id).get_talent_effects()

        club.add_talent_effects(talent_effects_1)
        club.add_talent_effects(talent_effects_2)
        club.add_talent_effects(talent_effects_3)
        club.add_talent_effects(talent_effects_4)

        config_inspire_level_addition, config_inspire_step_addition = ins.get_addition_config()

        for obj in self.formation_staffs:
            obj.config_inspire_level_addition = config_inspire_level_addition
            obj.config_inspire_step_addition = config_inspire_step_addition
            obj.calculate()

    @property
    def power(self):
        p = 0
        for s in self.formation_staffs:
            p += s.power

        return p

    def make_protobuf(self):
        msg = MsgPlunderFormation()
        msg.way = self.way_id

        msg.power = self.power

        sm = StaffManger(self.server_id, self.char_id)

        for k, v in self.doc['slots'].iteritems():
            msg_slot = msg.formation.add()
            msg_slot.slot_id = int(k)
            if v['staff_id']:
                msg_slot.status = FORMATION_SLOT_USE
                msg_slot.staff_id = v['staff_id']
                msg_slot.unit_id = v['unit_id']
                if v['unit_id']:
                    msg_slot.position = self.doc['position'].index(int(k))
                else:
                    msg_slot.position = -1

                msg_slot.staff_oid = sm.get_staff_object(v['staff_id']).oid
            else:
                msg_slot.status = FORMATION_SLOT_EMPTY

        return msg


class PlunderFormationWay1(PlunderFormation):
    __slots__ = []
    MONGO_COLLECTION = MongoPlunderFormationWay1


class PlunderFormationWay2(PlunderFormation):
    __slots__ = []
    MONGO_COLLECTION = MongoPlunderFormationWay2


class PlunderFormationWay3(PlunderFormation):
    __slots__ = []
    MONGO_COLLECTION = MongoPlunderFormationWay3


WAY_MAP = {
    1: PlunderFormationWay1,
    2: PlunderFormationWay2,
    3: PlunderFormationWay3,
}


def get_station_next_reward_at():
    now = arrow.utcnow().to(settings.TIME_ZONE)
    if now.hour >= 20:
        # 第二天
        now = now.replace(days=1)

    reward_at = arrow.Arrow(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=20,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=now.tzinfo
    )

    return reward_at.timestamp


PLUNDER_AUTO_ADD_HOUR = [21, 18, 15, 12, 9, 6]


def get_plunder_times_next_recover_at():
    now = arrow.utcnow().to(settings.TIME_ZONE)
    for index, hour in enumerate(PLUNDER_AUTO_ADD_HOUR):
        if now.hour >= hour:
            next_hour = PLUNDER_AUTO_ADD_HOUR[index - 1]
            break
    else:
        next_hour = PLUNDER_AUTO_ADD_HOUR[-1]

    recover_at = arrow.Arrow(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=next_hour,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=now.tzinfo
    )

    if now.hour > next_hour:
        # next day
        recover_at = recover_at.replace(days=1)

    return recover_at.timestamp


def check_club_level(silence=True):
    def deco(fun):
        def wrap(self, *args, **kwargs):
            """

            :type self: Plunder
            """

            if self.club_level < PLUNDER_ACTIVE_CLUB_LEVEL:
                if silence:
                    return

                raise GameException(ConfigErrorMessage.get_error_id("CLUB_LEVEL_NOT_ENOUGH"))

            return fun(self, *args, **kwargs)

        return wrap

    return deco


def check_plunder_in_process(fun):
    def deco(self, *args, **kwargs):
        """

        :type self: Plunder
        """
        if self.doc['matching']['id']:
            raise GameException(ConfigErrorMessage.get_error_id("PLUNDER_IN_PROGRESS"))

        return fun(self, *args, **kwargs)

    return deco


def is_npc(_id):
    return str(_id).startswith('npc:')


class PlunderTimesBuyInfo(object):
    __slots__ = ['buy_times', 'remained_buy_times', 'buy_cost']

    def __init__(self, server_id, char_id):
        vip = VIP(server_id, char_id)

        self.buy_times = ValueLogPlunderBuyTimes(server_id, char_id).count_of_today()
        self.remained_buy_times = vip.plunder_buy_times - self.buy_times
        if self.remained_buy_times < 0:
            self.remained_buy_times = 0

        self.buy_cost = ConfigPlunderBuyTimesCost.get_cost(self.buy_times + 1)


class PlunderNPC(object):
    __slots__ = ['id', 'name', 'station_level', 'ways_npc']

    def __init__(self, _id, name, station_level, ways_npc):
        self.id = _id
        self.name = name
        self.station_level = station_level
        self.ways_npc = ways_npc

    def get_station_level(self):
        return self.station_level

    def make_way_club(self, way_id):
        club = ConfigNPCFormation.get(self.ways_npc[way_id - 1])
        club.id = self.id
        club.name = self.name

        return club

    def got_plundered(self, from_id, win_ways):
        config = ConfigPlunderIncome.get(win_ways)
        config_station = ConfigBaseStationLevel.get(self.station_level)
        return config_station.get_product(config.percent)


class Plunder(object):
    __slots__ = ['server_id', 'char_id', 'club_level', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.club_level = get_club_property(self.server_id, self.char_id, 'level')

        self.doc = MongoPlunder.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoPlunder.document()
            self.doc['_id'] = self.char_id
            self.doc['plunder_remained_times'] = PLUNDER_TIMES_INIT_TIMES
            MongoPlunder.db(self.server_id).insert_one(self.doc)

        _, today_daily_reward_info = self.get_daily_reward_info()
        if not today_daily_reward_info:
            # 可以清理数据
            self.doc['daily_reward'] = {}
            MongoPlunder.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'daily_reward': {}
                }}
            )

    @classmethod
    def make_product(cls, server_id):
        def _make(doc):
            config = ConfigBaseStationLevel.get(doc['product_level'])
            items = config.get_product(100 - doc['loss_percent'])

            rc = ResourceClassification.classify(items)
            rc.add(server_id, doc['_id'], message="Plunder.make_product")

            MongoPlunder.db(server_id).update_one(
                {'_id': doc['_id']},
                {'$set': {
                    'product_level': doc['level'],
                    'loss_percent': 0,
                    # 'revenge_list': [],
                    'drop': rc.to_json(),
                }}
            )

        char_ids = Club.get_recent_login_char_ids(server_id)
        char_ids = [i for i in char_ids]
        docs = MongoPlunder.db(server_id).find(
            {'_id': {'$in': char_ids}},
            {'level': 1, 'product_level': 1, 'loss_percent': 1}
        )

        for d in docs:
            _make(d)

    @classmethod
    def auto_add_plunder_times(cls, server_id):
        char_ids = Club.get_recent_login_char_ids(server_id)
        char_ids = [i for i in char_ids]

        condition = {'$and': [
            {'_id': {'$in': char_ids}},
            {'plunder_remained_times': {'$lt': PLUNDER_TIMES_RECOVER_LIMIT}}
        ]}

        MongoPlunder.db(server_id).update_many(
            condition,
            {'$inc': {'plunder_remained_times': 1}}
        )

    @check_club_level(silence=True)
    def try_initialize(self):
        if self.doc['active']:
            return

        ways = [self.get_way_object(1), self.get_way_object(2), self.get_way_object(3)]
        club = Club(self.server_id, self.char_id)

        formation_staffs = club.formation_staffs
        """:type: list[core.staff.Staff]"""

        way_index = 0
        slot_id = 1

        for s in formation_staffs:
            ways[way_index].set_staff(slot_id, s.id)
            if s.unit:
                ways[way_index].set_unit(slot_id, s.unit.id)

            if way_index == 2:
                way_index = 0
                slot_id += 1
            else:
                way_index += 1

        self.doc['active'] = True
        MongoPlunder.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'active': True
            }}
        )

        self.send_formation_notify()

    def get_way_object(self, way_id):
        """

        :rtype: PlunderFormation
        """
        try:
            way_class = WAY_MAP[way_id]
        except KeyError:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        return way_class(self.server_id, self.char_id, way_id)

    def make_way_club(self, way_id):
        """

        :rtype: core.abstract.AbstractClub
        """
        way = self.get_way_object(way_id)

        club = Club(self.server_id, self.char_id, load_staffs=False)
        club.formation_staffs = way.formation_staffs
        return club

    def find_way_id_by_staff_id(self, staff_id):
        for i in [1, 2, 3]:
            if self.get_way_object(i).is_staff_in_formation(staff_id):
                return i

        return 0

    @check_club_level(silence=False)
    @check_plunder_in_process
    def set_staff(self, way_id, slot_id, staff_id):
        way_list = [1, 2, 3]
        if way_id not in way_list:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if slot_id not in [1, 2, 3]:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        way_list.remove(way_id)
        for i in way_list:
            w = self.get_way_object(i)
            w.try_unset_staff(staff_id)

        w = self.get_way_object(way_id)
        w.set_staff(slot_id, staff_id)

        self.send_formation_notify()

    @check_club_level(silence=False)
    @check_plunder_in_process
    def set_unit(self, way_id, slot_id, unit_id):
        if slot_id not in [1, 2, 3]:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        w = self.get_way_object(way_id)
        w.set_unit(slot_id, unit_id)
        self.send_formation_notify()

    def get_search_cd(self):
        return PlunderSearchCD(self.server_id, self.char_id).get_cd_seconds()

    def set_search_cd(self):
        cd = GlobalConfig.value("PLUNDER_SEARCH_CD")
        PlunderSearchCD(self.server_id, self.char_id).set(cd)

    @check_club_level(silence=False)
    @check_plunder_in_process
    def search(self, check_cd=True, replace_search_index=None, send_notify=True):
        if check_cd and self.get_search_cd():
            raise GameException(ConfigErrorMessage.get_error_id("PLUNDER_SEARCH_IN_CD"))

        def _query_real(_level_low, _level_high):
            _skip_char_ids = [_s['id'] for _s in self.doc['search']]
            _skip_char_ids.append(self.char_id)

            _condition = {'$and': [
                {'_id': {'$nin': _skip_char_ids}},
                {'level': {'$gte': _level_low}},
                {'level': {'$lte': _level_high}}
            ]}

            _docs = MongoCharacter.db(self.server_id).find(_condition, {'_id': 1})
            _ids = []
            for _doc in _docs:
                _ids.append(_doc['_id'])

            return _ids

        level_low = self.club_level - GlobalConfig.value("PLUNDER_SEARCH_LEVEL_RANGE_LOW")
        level_high = self.club_level + GlobalConfig.value("PLUNDER_SEARCH_LEVEL_RANGE_HIGH")

        if level_low < PLUNDER_ACTIVE_CLUB_LEVEL:
            level_low = PLUNDER_ACTIVE_CLUB_LEVEL

        real_ids = _query_real(level_low, level_high)
        # filter by loss_percent
        condition = {'$and': [
            {'_id': {'$in': real_ids}},
            {'loss_percent': {'$lt': PLUNDER_MAX_LOST}}
        ]}

        docs = MongoPlunder.db(self.server_id).find(condition, {'_id': 1})
        result_ids = []
        for doc in docs:
            if PlunderMatchCD(self.server_id, self.char_id, doc['_id']).get_cd_seconds():
                continue

            result_ids.append(doc['_id'])

        random.shuffle(result_ids)

        search_docs = []
        for i in result_ids:
            search_docs.append({'id': i, 'spied': False})
            if len(search_docs) == 2:
                break

        need_npc_amount = 2 - len(search_docs)
        if need_npc_amount:
            for i in range(need_npc_amount):
                config_plunder_npc = ConfigPlunderNPC.get_by_level(self.club_level)
                npc_doc = config_plunder_npc.to_doc(self.doc['level'])

                search_docs.append(npc_doc)

        if replace_search_index:
            self.doc['search'][replace_search_index] = search_docs[0]
            updater = {
                'search.{0}'.format(replace_search_index): self.doc['search'][replace_search_index]
            }
        else:
            self.doc['search'] = search_docs
            updater = {'search': search_docs}

        MongoPlunder.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        if check_cd:
            self.set_search_cd()

        if send_notify:
            self.send_search_notify()

    def find_search_target_index_by_target_id(self, target_id):
        target_id = str(target_id)
        for index, s in enumerate(self.doc['search']):
            if str(s['id']) == target_id:
                return index

        raise GameException(ConfigErrorMessage.get_error_id("PLUNDER_CANNOT_FIND_TARGET"))

    def find_revenge_target_index_by_target_id(self, target_id):
        for index, (unique_id, _) in enumerate(self.doc['revenge_list']):
            if unique_id == target_id:
                return index

        raise GameException(ConfigErrorMessage.get_error_id("PLUNDER_CANNOT_FIND_TARGET"))

    @check_club_level(silence=False)
    @check_plunder_in_process
    def spy(self, target_id):
        index = self.find_search_target_index_by_target_id(target_id)
        if self.doc['search'][index]['spied']:
            return

        cost = [(money_text_to_item_id('diamond'), 5), ]

        rc = ResourceClassification.classify(cost)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id, message="Plunder.spy")

        self.doc['search'][index]['spied'] = True
        MongoPlunder.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'search.{0}.spied'.format(index): True
            }}
        )

        self.send_search_notify()

    def get_revenge_remained_times(self):
        today_times = ValueLogPlunderRevengeTimes(self.server_id, self.char_id).count_of_today()
        remained = REVENGE_MAX_TIMES - today_times
        if remained < 0:
            remained = 0

        return remained

    def buy_plunder_times(self):
        info = PlunderTimesBuyInfo(self.server_id, self.char_id)
        if not info.remained_buy_times:
            raise GameException(ConfigErrorMessage.get_error_id("PLUNDER_NO_BUY_TIMES"))

        cost = [(money_text_to_item_id('diamond'), info.buy_cost), ]

        rc = ResourceClassification.classify(cost)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id, message="Plunder.buy_plunder_times")

        ValueLogPlunderBuyTimes(self.server_id, self.char_id).record()

        self.doc['plunder_remained_times'] += 1
        MongoPlunder.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'plunder_remained_times': self.doc['plunder_remained_times']
            }}
        )
        self.send_plunder_times_notify()

    @check_club_level(silence=False)
    def plunder_start(self, _id, tp, formation_slots=None, win=None):
        if tp not in [PLUNDER_TYPE_PLUNDER, PLUNDER_TYPE_REVENGE]:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        for i in [0, 1, 2]:
            if self.doc['matching']['result'][i] == 0:
                way = i + 1
                break
        else:
            # 都打完了
            raise GameException(ConfigErrorMessage.get_error_id("PLUNDER_MATCH_ALL_FINISHED"))

        target_id = self.doc['matching']['id']
        if not target_id:
            if tp == PLUNDER_TYPE_PLUNDER:
                _index = self.find_search_target_index_by_target_id(_id)
                target_id = self.doc['search'][_index]['id']
            else:
                _index = self.find_revenge_target_index_by_target_id(_id)
                target_id = self.doc['revenge_list'][_index][0]
        else:
            # 要保证target_id 一样
            if str(target_id) != _id:
                raise GameException(ConfigErrorMessage.get_error_id("PLUNDER_TARGET_ID_NOT_SAME"))

        updater = {}
        if not self.doc['matching']['id']:
            self.doc['matching']['id'] = target_id
            self.doc['matching']['tp'] = tp
            updater['matching.id'] = target_id
            updater['matching.tp'] = tp

        if way == 1:
            # 开始的第一路，这时候要判断次数
            if tp == PLUNDER_TYPE_PLUNDER:
                if not self.doc['plunder_remained_times']:
                    self.buy_plunder_times()

                PlunderMatchCD(self.server_id, self.char_id, target_id).set(GlobalConfig.value("PLUNDER_MATCH_CD"))

            else:
                if not self.get_revenge_remained_times():
                    raise GameException(ConfigErrorMessage.get_error_id("PLUNDER_REVENGE_NO_TIMES"))

                self.send_revenge_notify()

        if updater:
            MongoPlunder.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': updater}
            )

        if win is not None:
            self.plunder_report(way, win)
            return None

        my_way = self.get_way_object(way)
        if formation_slots:
            my_way.sync_slots(formation_slots)
            my_way.load_formation_staffs()
            self.send_formation_notify()

        my_club = Club(self.server_id, self.char_id, load_staffs=False)
        my_club.formation_staffs = my_way.formation_staffs

        match = ClubMatch(my_club, None)
        msg = match.start(auto_load_staffs=False)
        msg.key = str(way)
        msg.map_name = GlobalConfig.value_string("MATCH_MAP_PLUNDER")

        return msg

    @check_club_level(silence=False)
    def plunder_report(self, key, win):
        try:
            way = int(key)
            assert way in [1, 2, 3]
        except:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        way_index = way - 1
        result = 1 if win else 2

        target_id = self.doc['matching']['id']

        if not target_id:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        updater = {}
        self.doc['matching']['result'][way_index] = result
        updater['matching.result.{0}'.format(way_index)] = result

        if win:
            daily_key, info = self.get_daily_reward_info()
            win_ways = info.get('win_ways', 0)
            info['win_ways'] = win_ways + 1
            self.doc['daily_reward'] = {daily_key: info}
            updater['daily_reward'] = {daily_key: info}

        MongoPlunder.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_plunder_daily_reward_notify()
        self.send_result_notify()

    @check_club_level(silence=False)
    def get_reward(self):
        target_id = self.doc['matching']['id']
        tp = self.doc['matching']['tp']
        result = self.doc['matching']['result']

        if not target_id:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if 0 in result:
            raise GameException(ConfigErrorMessage.get_error_id("PLUNDER_MATCH_NOT_FINISH_CANNOT_GET_REWARD"))

        self.doc['matching'] = {
            'id': 0,
            'tp': 0,
            'result': [0, 0, 0],
        }

        updater = {
            'matching': self.doc['matching']
        }

        # NOTE: real target id
        plunder_got = []
        win_ways = sum([i for i in result if i == 1])

        config = ConfigPlunderIncome.get(win_ways)
        plunder_got.append((STATION_EXP_ID, config.exp))

        if tp == PLUNDER_TYPE_PLUNDER:
            real_id = target_id
            search_index = self.find_search_target_index_by_target_id(target_id)

            data = self.doc['search'][search_index]
            self.search(check_cd=False, replace_search_index=search_index)

            if is_npc(real_id):
                target_plunder = PlunderNPC(data['id'], data['name'], data['station_level'], data['ways_npc'])
            else:
                target_plunder = Plunder(self.server_id, real_id)
                plunder_got.extend(config.get_extra_income())

            _got = target_plunder.got_plundered(self.char_id, win_ways)
            plunder_got.extend(_got)

            ValueLogPlunderTimes(self.server_id, self.char_id).record()
            self.doc['plunder_remained_times'] -= 1
            updater['plunder_remained_times'] = self.doc['plunder_remained_times']

        else:
            revenge_index = self.find_revenge_target_index_by_target_id(target_id)
            _, real_id = self.doc['revenge_list'].pop(revenge_index)
            updater['revenge_list'] = self.doc['revenge_list']

            ValueLogPlunderRevengeTimes(self.server_id, self.char_id).record()
            self.send_revenge_notify()

        MongoPlunder.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_result_notify()
        self.send_plunder_times_notify()

        rc = ResourceClassification.classify(plunder_got)
        rc.add(self.server_id, self.char_id, message="Plunder.get_reward")
        return result, rc

    def got_plundered(self, from_id, win_ways):
        config = ConfigPlunderIncome.get(win_ways)

        if win_ways > 0:
            revenge_item = (make_string_id(), from_id)

            self.doc['loss_percent'] += config.percent
            if self.doc['loss_percent'] > PLUNDER_MAX_LOST:
                self.doc['loss_percent'] = PLUNDER_MAX_LOST

            self.doc['revenge_list'].append(revenge_item)
            while len(self.doc['revenge_list']) > 20:
                self.doc['revenge_list'].pop(0)

            MongoPlunder.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'loss_percent': self.doc['loss_percent'],
                    'revenge_list': self.doc['revenge_list'],
                }}
            )

            self.send_revenge_notify()
            self.send_station_notify()

        config_station = ConfigBaseStationLevel.get(self.doc['product_level'])
        return config_station.get_product(config.percent)

    def get_station_level(self):
        return self.doc['level']

    def add_station_exp(self, exp):
        self.doc['exp'] += exp

        old_level = self.doc['level']

        while True:
            config = ConfigBaseStationLevel.get(self.doc['level'])
            if self.doc['level'] == ConfigBaseStationLevel.MAX_LEVEL:
                if self.doc['exp'] > config.exp:
                    self.doc['exp'] = config.exp

                break

            if self.doc['exp'] < config.exp:
                break

            self.doc['level'] += 1
            self.doc['exp'] -= config.exp

        MongoPlunder.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'level': self.doc['level'],
                'exp': self.doc['exp'],
            }}
        )

        self.send_station_notify()
        return self.doc['level'] - old_level

    def get_daily_reward_info(self):
        key = get_start_time_of_today().format("YYYY-MM-DD")
        return key, self.doc.get('daily_reward', {}).get(key, {})

    def daily_reward_get(self, _id):
        config = ConfigPlunderDailyReward.get(_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        key, info = self.get_daily_reward_info()
        win_ways = info.get('win_ways', 0)
        got_list = info.get('got_list', [])

        if _id in got_list:
            raise GameException(ConfigErrorMessage.get_error_id("PLUNDER_DAILY_REWARD_ALREADY_GOT"))

        if win_ways < _id:
            raise GameException(ConfigErrorMessage.get_error_id("PLUNDER_DAILY_REWARD_NOT_ENOUGH"))

        rc = ResourceClassification.classify(config.reward)
        rc.add(self.server_id, self.char_id, message="Plunder.daily_reward_get:{0}".format(_id))

        got_list.append(_id)
        info['got_list'] = got_list

        self.doc['daily_reward'] = {key: info}
        MongoPlunder.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'daily_reward': {key: info}
            }}
        )

        self.send_plunder_daily_reward_notify(info=info)
        return rc

    @check_club_level(silence=False)
    def get_station_product(self):
        drop = self.doc.get('drop', '')
        if not drop:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        rc = ResourceClassification.load_from_json(drop)
        rc.add(self.server_id, self.char_id, message="Plunder.get_station_product")
        self.doc['drop'] = ''
        MongoPlunder.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'drop': ''
            }}
        )

        self.send_station_notify()
        return rc

    @check_club_level(silence=True)
    def send_formation_notify(self):
        notify = PlunderFormationNotify()
        for i in [1, 2, 3]:
            notify_way = notify.formation.add()
            w = self.get_way_object(i)
            notify_way.MergeFrom(w.make_protobuf())

        MessagePipe(self.char_id).put(msg=notify)

    @check_club_level(silence=True)
    def send_search_notify(self):
        if not self.doc['search']:
            try:
                self.search(send_notify=False)
            except GameException:
                pass

        notify = PlunderSearchNotify()
        notify.cd = self.get_search_cd()

        for s in self.doc['search']:
            notify_target = notify.target.add()
            notify_target.id = str(s['id'])
            notify_target.spied = s['spied']
            notify_target.is_npc = is_npc(s['id'])

            if str(s['id']).startswith('npc:'):
                target_plunder = PlunderNPC(s['id'], s['name'], s['station_level'], s['ways_npc'])
            else:
                target_plunder = Plunder(self.server_id, s['id'])

            notify_target.station_level = target_plunder.get_station_level()

            for way in [1, 2, 3]:
                notify_target_troop = notify_target.troop.add()
                club = target_plunder.make_way_club(way)
                notify_target_troop.MergeFrom(ClubMatch.make_club_troop_msg(club))
        MessagePipe(self.char_id).put(msg=notify)

    @check_club_level(silence=True)
    def send_result_notify(self):
        notify = PlunderResultNotify()
        if self.doc['matching']['id']:
            notify.id = str(self.doc['matching']['id'])
            notify.result.extend(self.doc['matching']['result'])

        MessagePipe(self.char_id).put(msg=notify)

    @check_club_level(silence=True)
    def send_plunder_times_notify(self):
        ti = PlunderTimesBuyInfo(self.server_id, self.char_id)

        notify = PlunderTimesNotify()
        notify.max_times = PLUNDER_TIMES_RECOVER_LIMIT
        notify.remained_times = self.doc['plunder_remained_times']
        notify.buy_cost = ti.buy_cost
        notify.remained_buy_times = ti.remained_buy_times
        notify.next_recover_at = get_plunder_times_next_recover_at()

        MessagePipe(self.char_id).put(msg=notify)

    @check_club_level(silence=True)
    def send_plunder_daily_reward_notify(self, info=None):
        if info is None:
            _, info = self.get_daily_reward_info()

        win_ways = info.get('win_ways', 0)
        got_list = info.get('got_list', [])

        notify = PlunderDailyRewardNotify()

        notify.win_ways = win_ways
        for i in ConfigPlunderDailyReward.INSTANCES.keys():
            notify_reward = notify.reward.add()
            notify_reward.id = i
            if i in got_list:
                notify_reward.status = 2
            elif win_ways >= i:
                notify_reward.status = 1
            else:
                notify_reward.status = 0

        MessagePipe(self.char_id).put(msg=notify)

    @check_club_level(silence=True)
    def send_station_notify(self):
        notify = BaseStationNotify()
        notify.level = self.doc['level']
        notify.exp = self.doc['exp']
        notify.next_reward_at = get_station_next_reward_at()

        drop = self.doc.get('drop', '')
        if drop:
            notify.drop.MergeFrom(ResourceClassification.load_from_json(drop).make_protomsg())

        notify.product_level = self.doc['product_level']
        notify.product_lost_percent = self.doc['loss_percent']
        MessagePipe(self.char_id).put(msg=notify)

    @check_club_level(silence=True)
    def send_revenge_notify(self):
        notify = PlunderRevengeNotify()
        notify.remained_times = self.get_revenge_remained_times()
        for unique_id, real_id in self.doc['revenge_list']:
            notify_target = notify.target.add()
            notify_target.id = unique_id

            club = Club(self.server_id, real_id, load_staffs=False)
            target_plunder = Plunder(self.server_id, real_id)
            notify_target.name = club.name

            for way_id in [1, 2, 3]:
                way_object = target_plunder.get_way_object(way_id)
                club.formation_staffs = way_object.formation_staffs

                notify_target_troop = notify_target.troop.add()
                notify_target_troop.MergeFrom(ClubMatch.make_club_troop_msg(club))

        MessagePipe(self.char_id).put(msg=notify)


class SpecialEquipmentGenerator(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.doc = MongoSpecialEquipment.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoSpecialEquipment.document()
            self.doc['_id'] = self.char_id
            MongoSpecialEquipment.db(self.server_id).insert_one(self.doc)

    def generate(self, bag_slot_id, tp):
        if self.doc['item_id']:
            raise GameException(ConfigErrorMessage.get_error_id("SPECIAL_EQUIPMENT_IS_IN_PROCESS"))

        if tp not in [SPECIAL_EQUIPMENT_GENERATE_NORMAL, SPECIAL_EQUIPMENT_GENERATE_ADVANCE]:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        bag = Bag(self.server_id, self.char_id)
        slot = bag.get_slot(bag_slot_id)
        item_id = slot['item_id']
        config = ConfigEquipmentSpecialGenerate.get(item_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if tp == SPECIAL_EQUIPMENT_GENERATE_NORMAL:
            cost = config.normal_cost
        else:
            cost = config.advance_cost

        rc = ResourceClassification.classify(cost)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id, message="SpecialEquipmentGenerator.generate:{0}".format(tp))

        bag.remove_by_slot_id(slot_id=bag_slot_id, amount=1)

        finish_at = arrow.utcnow().timestamp + config.minutes * 60

        self.doc['item_id'] = item_id
        self.doc['finish_at'] = finish_at
        self.doc['tp'] = tp

        MongoSpecialEquipment.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'item_id': self.doc['item_id'],
                'finish_at': self.doc['finish_at'],
                'tp': self.doc['tp'],
            }}
        )

        self.send_notify()

    def speedup(self):
        if not self.doc['item_id']:
            raise GameException(ConfigErrorMessage.get_error_id("SPECIAL_EQUIPMENT_NOT_IN_PROCESS"))

        seconds = self.doc['finish_at'] - arrow.utcnow().timestamp
        if seconds <= 0:
            raise GameException(ConfigErrorMessage.get_error_id("SPECIAL_EQUIPMENT_ALREADY_FINISHED"))

        minutes, remained = divmod(seconds, 60)
        if remained:
            minutes += 1

        diamond = minutes * GlobalConfig.value("EQUIPMENT_SPECIAL_SPEEDUP_PARAM") * 0.1
        diamond = int(diamond)
        cost = [(money_text_to_item_id('diamond'), diamond)]

        rc = ResourceClassification.classify(cost)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id, message="SpecialEquipmentGenerator.speedup")

        # make sure is finished
        self.doc['finish_at'] = arrow.utcnow().timestamp - 1
        MongoSpecialEquipment.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'finish_at': self.doc['finish_at']
            }}
        )

        self.send_notify()

    def get_result(self):
        if not self.doc['item_id']:
            raise GameException(ConfigErrorMessage.get_error_id("SPECIAL_EQUIPMENT_NOT_IN_PROCESS"))

        if arrow.utcnow().timestamp < self.doc['finish_at']:
            raise GameException(ConfigErrorMessage.get_error_id("SPECIAL_EQUIPMENT_NOT_FINISH"))

        tp = self.doc['tp']
        score = self.doc['score'][str(tp)]
        growing = ConfigEquipmentSpecialScoreToGrowing.get_random_growing_by_score(tp, score)

        config_generate = ConfigEquipmentSpecialGenerate.get(self.doc['item_id'])

        if tp == SPECIAL_EQUIPMENT_GENERATE_NORMAL:
            equip_id = random.choice(config_generate.normal_generate)
            if growing >= GlobalConfig.value("EQUIPMENT_SPECIAL_NORMAL_SCORE_RESET_AT"):
                new_score = 0
            else:
                new_score = score + 1
        else:
            equip_id = random.choice(config_generate.advance_generate)
            if growing >= GlobalConfig.value("EQUIPMENT_SPECIAL_ADVANCE_SCORE_RESET_AT"):
                new_score = 0
            else:
                new_score = score + 1

        config_property = ConfigEquipmentSpecialGrowingProperty.get_by_growing(growing)
        config_equipment = ConfigEquipmentSpecial.get(equip_id)

        properties = []
        for k, v in PROPERTY_TO_NAME_MAP.iteritems():
            if k in SPECIAL_EQUIPMENT_BASE_PROPERTY:
                continue

            if getattr(config_equipment, v, 0):
                properties.append(k)

        equip_properties = []
        for _ in config_property.property_active_levels:
            p = random.choice(properties)
            equip_properties.append(p)

        equip_skills = []
        for _ in config_property.skill_active_levels:
            s = random.choice(config_equipment.skills)
            equip_skills.append(s)

        equip_obj = Equipment.initialize_for_special(equip_id, self.doc['item_id'], tp, growing, equip_properties,
                                                     equip_skills)
        bag = Bag(self.server_id, self.char_id)
        bag.add_equipment_object(equip_obj)

        self.doc['item_id'] = 0
        self.doc['finish_at'] = 0
        self.doc['tp'] = 0
        self.doc['score'][str(tp)] = new_score

        MongoSpecialEquipment.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'item_id': 0,
                'finish_at': 0,
                'tp': 0,
                'score.{0}'.format(tp): new_score
            }}
        )

        ValueLogSpecialEquipmentGenerateTimes(self.server_id, self.char_id).record()
        self.send_notify()

        return equip_obj

    def send_notify(self):
        notify = SpecialEquipmentGenerateNotify()
        notify.id = self.doc['item_id']
        notify.finish_timestamp = self.doc['finish_at']
        tp = self.doc['tp']
        if not tp:
            tp = SPECIAL_EQUIPMENT_GENERATE_NORMAL

        notify.tp = tp

        MessagePipe(self.char_id).put(msg=notify)
