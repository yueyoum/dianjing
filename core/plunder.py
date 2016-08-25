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
)

from core.club import get_club_property, Club
from core.formation import BaseFormation
from core.staff import StaffManger, Staff
from core.unit import UnitManager
from core.cooldown import PlunderSearchCD
from core.match import ClubMatch
from core.value_log import ValueLogPlunderRevengeTimes, ValueLogPlunderTimes, ValueLogPlunderBuyTimes
from core.resource import ResourceClassification, STATION_EXP_ID, money_text_to_item_id

from utils.message import MessagePipe
from utils.functional import make_string_id

from config import ConfigErrorMessage, ConfigBaseStationLevel, ConfigPlunderBuyTimesCost, ConfigPlunderIncome

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
)

from protomsg.formation_pb2 import FORMATION_SLOT_EMPTY, FORMATION_SLOT_USE

PLUNDER_ACTIVE_CLUB_LEVEL = 15
PLUNDER_TIMES_INIT_LIMIT = 100
REVENGE_MAX_TIMES = 10


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

    def set_unit(self, slot_id, unit_id, staff_calculate=True):
        super(PlunderFormation, self).set_unit(slot_id, unit_id, staff_calculate=staff_calculate)
        self.load_formation_staffs()

    def load_formation_staffs(self):
        # TODO talents
        self.formation_staffs = []

        sm = StaffManger(self.server_id, self.char_id)
        um = UnitManager(self.server_id, self.char_id)

        in_formation_staffs = self.in_formation_staffs()

        staffs = sm.get_staffs_data()

        for k, v in in_formation_staffs.iteritems():
            obj = Staff(self.server_id, self.char_id, k, staffs[k])
            obj.policy = in_formation_staffs[k]['policy']
            obj.formation_position = in_formation_staffs[k]['position']

            unit_id = in_formation_staffs[k]['unit_id']
            if unit_id:
                obj.set_unit(um.get_unit_object(unit_id))

            obj.calculate()
            self.formation_staffs.append(obj)

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


class PlunderTimesInformation(object):
    __slots__ = ['server_id', 'char_id', 'current_times', 'remained_times', 'max_times', 'buy_times', 'buy_cost']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.max_times = PLUNDER_TIMES_INIT_LIMIT
        self.current_times = ValueLogPlunderTimes(self.server_id, self.char_id).count_of_today()
        self.buy_times = ValueLogPlunderBuyTimes(self.server_id, self.char_id).count_of_today()

        self.remained_times = 0
        self.buy_cost = 0

        self.update()

    def update(self):
        self.max_times = PLUNDER_TIMES_INIT_LIMIT + self.buy_times

        self.remained_times = self.max_times - self.current_times
        if self.remained_times < 0:
            self.remained_times = 0

        self.buy_cost = ConfigPlunderBuyTimesCost.get_cost(self.buy_times + 1)

    def add_plunder_times(self):
        ValueLogPlunderTimes(self.server_id, self.char_id).record()
        self.current_times += 1
        self.update()

    def add_buy_times(self):
        ValueLogPlunderBuyTimes(self.server_id, self.char_id).record()
        self.buy_times += 1
        self.update()

    def send_plunder_times_notify(self):
        notify = PlunderTimesNotify()
        notify.max_times = self.max_times
        notify.remained_times = self.remained_times
        notify.buy_cost = self.buy_cost
        # TODO
        notify.next_recover_at = 0

        MessagePipe(self.char_id).put(msg=notify)


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
            MongoPlunder.db(self.server_id).insert_one(self.doc)

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
                ways[way_index].set_unit(slot_id, s.unit.id, staff_calculate=False)

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

    @check_club_level(silence=False)
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
    def set_unit(self, way_id, slot_id, unit_id):
        if slot_id not in [1, 2, 3]:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        w = self.get_way_object(way_id)
        w.set_unit(slot_id, unit_id, staff_calculate=False)
        self.send_formation_notify()

    @check_club_level(silence=False)
    @check_plunder_in_process
    def search(self, replace_search_index=None):
        def _query(level_low, level_high):
            if level_low < PLUNDER_ACTIVE_CLUB_LEVEL:
                level_low = PLUNDER_ACTIVE_CLUB_LEVEL

            _condition = {'$and': [
                {'_id': {'$ne': self.char_id}},
                {'level': {'$gte': level_low}},
                {'level': {'$lte': level_high}}
            ]}

            _docs = MongoCharacter.db(self.server_id).find(_condition, {'_id': 1})
            _ids = []
            for _doc in _docs:
                _ids.append(_doc['_id'])

            return _ids

        level_range = [5, 10, 50, 100, 1000]
        for i in level_range:
            ids = _query(self.club_level - i, self.club_level + i)
            # filter by loss_percent
            condition = {'$and': [
                {'_id': {'$in': ids}},
                {'loss_percent': {'$lte': 60}}
            ]}

            docs = MongoPlunder.db(self.server_id).find(condition, {'_id': 1})
            ids = [doc['_id'] for doc in docs]
            if len(ids) >= 2:
                break
        else:
            raise GameException(ConfigErrorMessage.get_error_id("PLUNDER_SEARCH_NO_RESULT"))

        random.shuffle(ids)

        if replace_search_index:
            self.doc['search'][replace_search_index] = {'id': ids[0], 'spied': False}
            updater = {
                'search.{0}'.format(replace_search_index): self.doc['search'][replace_search_index]
            }
        else:
            result = [
                {'id': ids[0], 'spied': False},
                {'id': ids[1], 'spied': False},
            ]

            self.doc['search'] = result
            updater = {'search': result}

        MongoPlunder.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_search_notify()

    def find_search_target_index_by_target_id(self, target_id):
        for index, s in enumerate(self.doc['search']):
            if s['id'] == target_id:
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
        info = PlunderTimesInformation(self.server_id, self.char_id)
        cost = [(money_text_to_item_id('diamond'), info.buy_cost), ]

        rc = ResourceClassification.classify(cost)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id)

        info.add_buy_times()
        info.send_plunder_times_notify()

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

        if way == 1:
            # 开始的第一路，这时候要判断次数
            if tp == PLUNDER_TYPE_PLUNDER:
                info = PlunderTimesInformation(self.server_id, self.char_id)
                info.add_plunder_times()

                if not info.remained_times:
                    cost = [(money_text_to_item_id('diamond'), info.buy_cost)]
                    rc = ResourceClassification.classify(cost)
                    rc.check_exist(self.server_id, self.char_id)
                    rc.remove(self.server_id, self.char_id)

                    info.add_buy_times()

                info.send_plunder_times_notify()
                #
                # if not self.get_plunder_remained_times():
                #     raise GameException(ConfigErrorMessage.get_error_id("PLUNDER_NO_TIMES"))
            else:
                if not self.get_revenge_remained_times():
                    raise GameException(ConfigErrorMessage.get_error_id("PLUNDER_REVENGE_NO_TIMES"))

                ValueLogPlunderRevengeTimes(self.server_id, self.char_id).record()
                self.send_revenge_notify()

        target_id = self.doc['matching']['id']
        if not target_id:
            if tp == PLUNDER_TYPE_PLUNDER:
                target_id = int(_id)
            else:
                _index = self.find_revenge_target_index_by_target_id(_id)
                target_id = self.doc['revenge_list'][_index][0]
        else:
            # 要保证target_id 一样
            if str(target_id) != _id:
                raise GameException(ConfigErrorMessage.get_error_id("PLUNDER_TARGET_ID_NOT_SAME"))

        if not self.doc['matching']['id']:
            self.doc['matching']['id'] = target_id
            self.doc['matching']['tp'] = tp
            MongoPlunder.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'matching.id': target_id,
                    'matching.tp': tp,
                }}
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
        msg = match.start()
        msg.key = str(way)

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

        self.doc['matching']['result'][way_index] = result

        MongoPlunder.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'matching.result.{0}'.format(way_index): result
            }}
        )

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

        if tp == PLUNDER_TYPE_PLUNDER:
            real_id = target_id
            search_index = self.find_search_target_index_by_target_id(target_id)
            self.search(replace_search_index=search_index)
        else:
            revenge_index = self.find_revenge_target_index_by_target_id(target_id)
            _, real_id = self.doc['revenge_list'].pop(revenge_index)
            updater['revenge_list'] = self.doc['revenge_list']

            self.send_revenge_notify()

        MongoPlunder.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_result_notify()

        win_ways = sum([i for i in result if i == 1])

        plunder_got = []
        if tp == PLUNDER_TYPE_PLUNDER:
            target_plunder = Plunder(self.server_id, real_id)
            _got = target_plunder.got_plundered(self.char_id, win_ways)
            plunder_got.extend(_got)

        config = ConfigPlunderIncome.get(win_ways)
        plunder_got.extend(config.get_extra_income())

        plunder_got.append((STATION_EXP_ID, config.exp))

        rc = ResourceClassification.classify(plunder_got)
        rc.add(self.server_id, self.char_id)
        return result, rc

    def got_plundered(self, from_id, win_ways):
        config = ConfigPlunderIncome.get(win_ways)
        revenge_item = (make_string_id(), from_id)

        self.doc['loss_percent'] += config.percent
        if self.doc['loss_percent'] > 60:
            self.doc['loss_percent'] = 60

        self.doc['revenge_list'].append(revenge_item)

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
                self.search()
            except GameException:
                pass

        notify = PlunderSearchNotify()
        notify.cd = PlunderSearchCD(self.server_id, self.char_id).get_cd_seconds()

        for s in self.doc['search']:
            target_plunder = Plunder(self.server_id, s['id'])

            notify_target = notify.target.add()
            notify_target.id = str(s['id'])
            notify_target.station_level = target_plunder.get_station_level()
            notify_target.spied = s['spied']

            for way in [1, 2, 3]:
                notify_target_troop = notify_target.troop.add()

                way_object = target_plunder.get_way_object(way)

                club = Club(self.server_id, s['id'], load_staffs=False)
                club.formation_staffs = way_object.formation_staffs

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
        info = PlunderTimesInformation(self.server_id, self.char_id)
        info.send_plunder_times_notify()

    @check_club_level(silence=True)
    def send_station_notify(self):
        notify = BaseStationNotify()
        notify.level = self.doc['level']
        notify.exp = self.doc['exp']
        notify.next_reward_at = get_station_next_reward_at()

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
        microsecond=0,
        tzinfo=now.tzinfo
    )

    return reward_at.timestamp
