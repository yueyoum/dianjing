# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       club
Date Created:   2015-07-03 15:09
Description:

"""
#
# import base64
# import dill
import arrow

from django.conf import settings

from core.mongo import MongoCharacter, MongoCharacterLoginLog
from core.abstract import AbstractClub
from core.signals import club_level_up_signal, task_condition_trig_signal
from core.statistics import FinanceStatistics

from dianjing.exception import GameException

from utils.message import MessagePipe
from utils.stdvalue import MAX_INT
from utils.functional import make_string_id

from config import (
    ConfigClubLevel,
    ConfigErrorMessage,
)

from config.settings import (
    CHAR_INIT_DIAMOND,
    CHAR_INIT_GOLD,
    CHAR_INIT_CRYSTAL,
    CHAR_INIT_GAS,
    CHAR_INIT_STAFFS,
)

from protomsg.club_pb2 import ClubNotify


def get_club_property(server_id, char_id, key, default_value=0):
    doc = MongoCharacter.db(server_id).find_one(
        {'_id': char_id},
        {key: 1}
    )

    return doc.get(key, default_value)


# 为了兼容任务条件
class _ClubProperty(object):
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def get_level(self):
        return get_club_property(self.server_id, self.char_id, 'level')


class Club(AbstractClub):
    __slots__ = []

    def __init__(self, server_id, char_id, load_staffs=True):
        super(Club, self).__init__()

        self.server_id = server_id
        self.char_id = char_id

        doc = MongoCharacter.db(self.server_id).find_one({'_id': self.char_id})
        assert doc is not None, "can not find char_id: {0}".format(self.char_id)

        self.id = self.char_id  # 玩家ID
        self.name = doc['name']  # 俱乐部名
        self.flag = doc['flag']  # 俱乐部旗帜
        self.level = doc['level']  # 俱乐部等级
        self.exp = doc['exp']
        self.gold = doc['gold']  # 游戏币
        self.diamond = doc['diamond']  # 钻石
        self.renown = doc['renown']

        self.crystal = doc['crystal']
        self.gas = doc['gas']

        if load_staffs:
            self.load_staffs()

    def load_staffs(self):
        from core.staff import StaffManger
        from core.formation import Formation

        self.formation_staffs = []

        sm = StaffManger(self.server_id, self.char_id)
        fm = Formation(self.server_id, self.char_id)

        for k in fm.in_formation_staffs():
            self.formation_staffs.append(sm.get_staff_object(k))

    def force_load_staffs(self, send_notify=False):
        from core.staff import StaffManger, Staff
        from core.formation import Formation
        from core.unit import UnitManager
        from core.talent import TalentManager
        from core.collection import Collection
        from core.party import Party
        from core.inspire import Inspire

        self.formation_staffs = []

        sm = StaffManger(self.server_id, self.char_id)
        fm = Formation(self.server_id, self.char_id)
        um = UnitManager(self.server_id, self.char_id)
        ins = Inspire(self.server_id, self.char_id)

        staffs = sm.get_staffs_data()
        in_formation_staffs = fm.in_formation_staffs()

        staff_objs = {}
        """:type: dict[str, core.staff.Staff]"""
        for k, v in staffs.items():
            staff_objs[k] = Staff(self.server_id, self.char_id, k, v)

        for k, v in staff_objs.iteritems():
            if k in in_formation_staffs:
                self.formation_staffs.append(v)

                v.policy = in_formation_staffs[k]['policy']
                v.formation_position = in_formation_staffs[k]['position']
                unit_id = in_formation_staffs[k]['unit_id']
                if unit_id:
                    v.set_unit(um.get_unit_object(unit_id))

        working_staff_oids = fm.working_staff_oids()

        for k in in_formation_staffs:
            staff_objs[k].check_qianban(working_staff_oids)
            staff_objs[k].add_self_talent_effect(self)

        talent_effects_1 = TalentManager(self.server_id, self.char_id).get_talent_effects()
        talent_effects_2 = Collection(self.server_id, self.char_id).get_talent_effects()
        talent_effects_3 = fm.get_talent_effects()
        talent_effects_4 = Party(self.server_id, self.char_id).get_talent_effects()

        self.add_talent_effects(talent_effects_1)
        self.add_talent_effects(talent_effects_2)
        self.add_talent_effects(talent_effects_3)
        self.add_talent_effects(talent_effects_4)

        config_inspire_level_addition, config_inspire_step_addition = ins.get_addition_config()

        for _, v in staff_objs.iteritems():
            v.config_inspire_level_addition = config_inspire_level_addition
            v.config_inspire_step_addition = config_inspire_step_addition
            v.calculate()
            v.make_cache()

        if send_notify:
            self.send_notify()
            in_formation_staff_ids = fm.in_formation_staffs().keys()
            sm.send_notify(ids=in_formation_staff_ids)

    @classmethod
    def create(cls, server_id, char_id, club_name, club_flag):
        from core.staff import StaffManger
        from core.formation import Formation

        doc = MongoCharacter.document()
        doc['_id'] = char_id
        doc['create_at'] = arrow.utcnow().timestamp

        doc['name'] = club_name
        doc['flag'] = club_flag
        doc['gold'] = CHAR_INIT_GOLD
        doc['diamond'] = CHAR_INIT_DIAMOND
        doc['crystal'] = CHAR_INIT_CRYSTAL
        doc['gas'] = CHAR_INIT_GAS

        sm = StaffManger(server_id, char_id)

        formation_init_data = []
        for staff_id, unit_id in CHAR_INIT_STAFFS:
            uid = sm.add(staff_id, send_notify=False, trig_signal=False)
            formation_init_data.append((uid, unit_id))

        fm = Formation(server_id, char_id)
        fm.initialize(formation_init_data)

        MongoCharacter.db(server_id).insert_one(doc)

    @classmethod
    def query_char_ids(cls, server_id, min_level=None, login_range=None):
        # 根据各种条件查询
        result_list = []

        if min_level:
            docs = MongoCharacter.db(server_id).find({'level': {'$gte': min_level}}, {'_id': 1})
            char_ids_1 = [d['_id'] for d in docs]

            result_list.append(char_ids_1)

        if login_range:
            condition = {'$and': [
                {'timestamp': {'$gte': login_range[0]}},
                {'timestamp': {'$lte': login_range[1]}}
            ]}

            char_ids_2 = MongoCharacterLoginLog.db(server_id).distinct(
                'char_id',
                condition
            )

            result_list.append(char_ids_2)

        if not result_list:
            raise RuntimeError("Club.query_char_ids with no condition")

        result = set(result_list[0])
        for i in range(1, len(result_list)):
            result &= set(result_list[i])

        return list(result)


    @classmethod
    def get_recent_login_char_ids(cls, server_id, recent_days=14, other_conditions=None):
        day_limit = arrow.utcnow().replace(days=-recent_days)
        timestamp = day_limit.timestamp

        condition = {'last_login': {'$gte': timestamp}}
        if other_conditions:
            condition = [condition]
            condition.extend(other_conditions)
            condition = {'$and': condition}

        doc = MongoCharacter.db(server_id).find(condition, {'_id': 1})
        for d in doc:
            yield d['_id']

    @classmethod
    def create_days(cls, server_id, char_id):
        # 从创建到现在是第几天。 从1开始
        doc = MongoCharacter.db(server_id).find_one(
            {'_id': char_id},
            {'create_at': 1}
        )

        create_at = arrow.get(doc['create_at']).to(settings.TIME_ZONE)
        now = arrow.utcnow().to(settings.TIME_ZONE)
        days = (now.date() - create_at.date()).days
        return days + 1

    @classmethod
    def days_since_last_login(cls, server_id, char_id):
        # 从最近一次登陆 到现在已经过了多少天
        doc = MongoCharacter.db(server_id).find_one(
            {'_id': char_id},
            {'last_login': 1}
        )

        last_login = arrow.get(doc['last_login']).to(settings.TIME_ZONE)
        now = arrow.utcnow().to(settings.TIME_ZONE)
        days = (now.date() - last_login.date()).days
        return days

    def set_login(self):
        from django.db.models import F
        from apps.character.models import Character as ModelCharacter

        now = arrow.utcnow()
        ModelCharacter.objects.filter(id=self.char_id).update(
            last_login=now.format("YYYY-MM-DD HH:mm:ssZ"),
            login_times=F('login_times') + 1,
        )
        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'last_login': now.timestamp}}
        )

        login_doc = MongoCharacterLoginLog.document()
        login_doc['_id'] = make_string_id()
        login_doc['char_id'] = self.char_id
        login_doc['timestamp'] = now.timestamp

        MongoCharacterLoginLog.db(self.server_id).insert_one(login_doc)


    def check_money(self, diamond=0, gold=0, crystal=0, gas=0, renown=0):
        if diamond > self.diamond:
            raise GameException(ConfigErrorMessage.get_error_id("DIAMOND_NOT_ENOUGH"))
        if gold > self.gold:
            raise GameException(ConfigErrorMessage.get_error_id("GOLD_NOT_ENOUGH"))
        if crystal > self.crystal:
            raise GameException(ConfigErrorMessage.get_error_id("CRYSTAL_NOT_ENOUGH"))
        if gas > self.gas:
            raise GameException(ConfigErrorMessage.get_error_id("GAS_NOT_ENOUGH"))
        if renown > self.renown:
            raise GameException(ConfigErrorMessage.get_error_id("RENOWN_NOT_ENOUGH"))

    def update(self, **kwargs):
        exp = kwargs.get('exp', 0)
        gold = kwargs.get('gold', 0)
        diamond = kwargs.get('diamond', 0)
        crystal = kwargs.get('crystal', 0)
        gas = kwargs.get('gas', 0)
        renown = kwargs.get('renown', 0)
        message = kwargs.get('message', "")

        self.gold += gold
        self.diamond += diamond
        self.exp += exp
        self.crystal += crystal
        self.gas += gas
        self.renown += renown

        if self.gold > MAX_INT:
            self.gold = MAX_INT
        if self.diamond > MAX_INT:
            self.diamond = MAX_INT
        if self.exp > MAX_INT:
            self.exp = MAX_INT
        if self.crystal > MAX_INT:
            self.crystal = MAX_INT
        if self.gas > MAX_INT:
            self.gas = MAX_INT
        if self.renown > MAX_INT:
            self.renown = MAX_INT

        if self.gold < 0:
            raise GameException(ConfigErrorMessage.get_error_id("GOLD_NOT_ENOUGH"))
        if self.diamond < 0:
            raise GameException(ConfigErrorMessage.get_error_id("DIAMOND_NOT_ENOUGH"))
        if self.crystal < 0:
            raise GameException(ConfigErrorMessage.get_error_id("CRYSTAL_NOT_ENOUGH"))
        if self.gas < 0:
            raise GameException(ConfigErrorMessage.get_error_id("GAS_NOT_ENOUGH"))
        if self.renown < 0:
            raise GameException(ConfigErrorMessage.get_error_id("RENOWN_NOT_ENOUGH"))

        # update
        level_changed = False
        while True:
            need_exp = ConfigClubLevel.get(self.level).exp
            if self.level >= ConfigClubLevel.MAX_LEVEL:
                if self.exp >= need_exp:
                    self.exp = need_exp
                    break

            if self.exp < need_exp:
                break

            self.exp -= need_exp
            self.level += 1
            level_changed = True

        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'level': self.level,
                'exp': self.exp,
                'gold': self.gold,
                'diamond': self.diamond,
                'crystal': self.crystal,
                'gas': self.gas,
                'renown': self.renown
            }}
        )

        if level_changed:
            club_level_up_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
                new_level=self.level
            )

            task_condition_trig_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
                condition_name='core.club._ClubProperty'
            )

        self.send_notify()

        if gold or diamond:
            FinanceStatistics(self.server_id, self.char_id).add_log(
                gold=gold,
                diamond=diamond,
                message=message
            )

    # def dumps(self):
    #     """
    #
    #     :rtype : str
    #     """
    #     return base64.b64encode(dill.dumps(self))
    #
    # @classmethod
    # def loads(cls, data):
    #     """
    #
    #     :rtype : Club
    #     """
    #     return dill.loads(base64.b64decode(data))

    def send_notify(self):
        msg = self.make_protomsg()
        notify = ClubNotify()
        notify.club.MergeFrom(msg)
        MessagePipe(self.char_id).put(notify)
