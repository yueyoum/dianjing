# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       cup
Date Created:   2015-08-26 15:16
Description:

"""

import calendar
import arrow
import dill
import base64

from pymongo.errors import DuplicateKeyError

from django.conf import settings
from dianjing.exception import GameException

from core.mongo import MongoCup, MongoCupClub, MongoCharacter
from core.abstract import AbstractClub
from core.club import Club
from core.match import ClubMatch
from core.signals import join_cup_signal

from utils.functional import make_string_id
from config import ConfigErrorMessage, ConfigNPC

from protomsg import cup_pb2
from protomsg.cup_pb2 import Cup as MessageCup


# 处理杯赛各阶段时间
CUP_PROCESS_PREPARE_DAY = 4         # 预选赛时间, 即截止报名时间
CUP_PROCESS_32_DAY = 5              # 32强决出时间, 每月5号
CUP_PROCESS_16_DAY = 10             # 16强决出时间, 每月10号
CUP_PROCESS_8_DAY = 15              # 8强决出时间, 每月15号
CUP_PROCESS_4_DAY = 20              # 8强决出时间, 每月20号
CUP_PROCESS_2_DAY = 25              # 半决赛时间, 每月25号
CUP_PROCESS_1_HOUR = 22             # 总决赛时间, 每月最后一天22点

# 服务器程序内部使用
CUP_PROCESS_APPLY = 1000  # 报名
CUP_PROCESS_PREPARE = 1001  # 预选赛

CUP_PROCESS_32 = 32  # 32强
CUP_PROCESS_16 = 16  # 16强
CUP_PROCESS_8 = 8  # 8强
CUP_PROCESS_4 = 4  # 4强    半决赛
CUP_PROCESS_2 = 2  # 2强    总决赛
CUP_PROCESS_1 = 1  # 结束

CUP_LEVELS = [
    CUP_PROCESS_32,
    CUP_PROCESS_16,
    CUP_PROCESS_8,
    CUP_PROCESS_4,
    CUP_PROCESS_2,
    CUP_PROCESS_1,
]


# 做一个映射避免修改消息，程序也要跟着改
CUP_PROCESS_TABLE = {
    CUP_PROCESS_APPLY: cup_pb2.CUP_PROCESS_APPLY,
    CUP_PROCESS_PREPARE: cup_pb2.CUP_PROCESS_PREPARE,
    CUP_PROCESS_32: cup_pb2.CUP_PROCESS_32,
    CUP_PROCESS_16: cup_pb2.CUP_PROCESS_16,
    CUP_PROCESS_8: cup_pb2.CUP_PROCESS_8,
    CUP_PROCESS_4: cup_pb2.CUP_PROCESS_4,
    CUP_PROCESS_2: cup_pb2.CUP_PROCESS_2,
    CUP_PROCESS_1: cup_pb2.CUP_PROCESS_1,
}


class CupNpcClub(AbstractClub):
    """
    NPC俱乐部基本属性
    """
    __slots__ = []

    def __init__(self, club_data):
        super(CupNpcClub, self).__init__()
        self.id = make_string_id()
        self.name = club_data['club_name']
        self.manager_name = club_data['manager_name']
        self.flag = club_data['club_flag']
        self.staffs = club_data['staffs']
        self.policy = 1

    def dumps(self):
        """

        :rtype: str
        """
        return base64.b64encode(dill.dumps(self))

    @classmethod
    def loads(cls, data):
        """

        :rtype: CupNpcClub
        """
        return dill.loads(base64.b64decode(data))


class CupClub(object):
    def __new__(cls, server_id, club_data):

        if club_data['is_npc']:
            return CupNpcClub.loads(club_data['data'])

        return Club.loads(club_data['data'])


class CupLevel(object):
    def __init__(self, year, month, lv):
        self.level = lv
        self.match_time = 0

        day = 1
        hour = 0
        if lv == CUP_PROCESS_APPLY:
            pass
        elif lv == CUP_PROCESS_PREPARE:
            day = CUP_PROCESS_PREPARE_DAY
        elif lv == CUP_PROCESS_32:
            day = CUP_PROCESS_32_DAY
        elif lv == CUP_PROCESS_16:
            day = CUP_PROCESS_16_DAY
        elif lv == CUP_PROCESS_8:
            day = CUP_PROCESS_8_DAY
        elif lv == CUP_PROCESS_4:
            day = CUP_PROCESS_4_DAY
        elif lv == CUP_PROCESS_2:
            day = CUP_PROCESS_2_DAY
        elif lv == CUP_PROCESS_1:
            day = calendar.monthrange(year, month)[1]
            hour = CUP_PROCESS_1_HOUR

        self.start_time = arrow.Arrow(year, month, day, hour, 0, 0, tzinfo=settings.TIME_ZONE)

    @classmethod
    def current_level(cls):
        now = arrow.utcnow().to(settings.TIME_ZONE)
        current_day = now.day
        last_day_of_this_month = calendar.monthrange(now.year, now.month)

        if current_day < CUP_PROCESS_PREPARE_DAY:
            # 1 ~ 3
            level = CUP_PROCESS_APPLY
        elif current_day < CUP_PROCESS_32_DAY:
            # 4
            level = CUP_PROCESS_PREPARE
        elif current_day < CUP_PROCESS_16_DAY:
            # 5 ~ 9
            level = CUP_PROCESS_32
        elif current_day < CUP_PROCESS_8_DAY:
            # 10 ~ 14
            level = CUP_PROCESS_16
        elif current_day < CUP_PROCESS_4_DAY:
            # 15 ~ 20
            level = CUP_PROCESS_8
        elif current_day < CUP_PROCESS_2_DAY:
            # 20 ~ 24
            level = CUP_PROCESS_4
        elif current_day < last_day_of_this_month:
            # 25 ~ last_day_of_this_month - 1
            level = CUP_PROCESS_2
        else:
            # last_day_of_this_month
            if now.hour <= CUP_PROCESS_1_HOUR:
                level = CUP_PROCESS_2
            else:
                level = CUP_PROCESS_1

        return cls(now.year, now.month, level)

    @classmethod
    def all_match_levels(cls):
        now = arrow.utcnow().to(settings.TIME_ZONE)
        result = []
        for lv in CUP_LEVELS:
            lv = cls(now.year, now.month, lv)
            if lv.level == CUP_PROCESS_APPLY or lv.level == CUP_PROCESS_PREPARE:
                continue

            result.append(lv)
        return result

    @classmethod
    def all_passed_match_levels(cls):
        now = arrow.utcnow().to(settings.TIME_ZONE)
        levels = cls.all_match_levels()
        return [lv for lv in levels if lv.start_time <= now]


class Cup(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    @staticmethod
    def new(server_id):
        cup_doc = MongoCup.db(server_id).find_one({'_id': 1}, {'levels.1': 1})
        club_name = ""
        if cup_doc['level'].get('1', 0):
            club_name = CupClub(server_id, cup_doc['level']['1']).name

        MongoCharacter.db(server_id).update_many(
            {'in_cup': True},
            {'$set': {'in_cup': False}}
        )

        MongoCupClub.db(server_id).drop()
        MongoCup.db(server_id).update_one(
            {'_id': 1},
            {
                '$set': {
                    'levels': {},
                    'last_champion': club_name,
                },
                '$inc': {
                    'order': 1
                }
            },
            upsert=True,
        )

    @staticmethod
    def prepare(server_id):
        chars = MongoCharacter.db(server_id).find({'in_cup': True}, {'_id': 1})
        char_ids = [c['_id'] for c in chars]
        if len(char_ids) < 32:
            need_npc_amount = 32 - len(char_ids)
            npcs = ConfigNPC.random_npcs(need_npc_amount, 1)
            npc_ids = []

            docs = []
            for n in npcs:
                npc_club = CupNpcClub(n)
                doc = MongoCupClub.document()
                doc['is_npc'] = True
                doc['_id'] = npc_club.id
                doc['data'] = npc_club.dumps()
                docs.append(doc)
                npc_ids.append(npc_club.id)

            for char_id in char_ids:
                doc = MongoCupClub.document()
                doc['is_npc'] = False
                doc['_id'] = char_id
                doc['data'] = ''
                docs.append(doc)

            MongoCupClub.db(server_id).insert_many(docs)

            insert_ids = []
            while len(insert_ids) < 32:
                if char_ids:
                    insert_ids.append(char_ids.pop(0))

                if npc_ids:
                    insert_ids.append(npc_ids.pop(0))

            MongoCup.db(server_id).update_one(
                {'_id': 1},
                {'$set': {'levels.{0}'.format(CUP_PROCESS_32): insert_ids}}
            )
        else:
            # TODO：报名人数高于32处理
            pass

    @staticmethod
    def match(server_id):
        all_passed_match_levels = CupLevel.all_passed_match_levels()

        cup_doc = MongoCup.db(server_id).find_one({'_id': 1})
        for index in range(1, len(all_passed_match_levels)):
            lv = all_passed_match_levels[index].level
            if str(lv) not in cup_doc['levels']:
                club_ids = cup_doc['levels'][str(all_passed_match_levels[index - 1].level)]

                current_level_club_ids = []
                for c in range(0, len(club_ids) - 1, 2):
                    club_one = MongoCupClub.db(server_id).find_one({'_id': club_ids[c]})
                    club_two = MongoCupClub.db(server_id).find_one({'_id': club_ids[c + 1]})

                    msg = ClubMatch(CupClub(server_id, club_one), CupClub(server_id, club_two)).start()
                    msg.key = ""
                    if msg.club_one_win:
                        current_level_club_ids.append(club_one['_id'])
                    else:
                        current_level_club_ids.append(club_two['_id'])

                MongoCup.db(server_id).update_one(
                    {'_id': 1},
                    {'$set': {
                        'levels.{0}'.format(lv): current_level_club_ids,
                    }}
                )

    @staticmethod
    def current_level():
        return CupLevel.current_level()

    @staticmethod
    def club_data_dumps(server_id):
        all_passed_match_levels = CupLevel.all_passed_match_levels()

        cup_doc = MongoCup.db(server_id).find_one({'_id': 1})
        club_ids = cup_doc['levels'][str(all_passed_match_levels[len(all_passed_match_levels)-1].level)]

        for club_info in MongoCupClub.db(server_id).find({'_id': {'$in': club_ids}}):
            if not club_info['is_npc']:
                MongoCupClub.db(server_id).update_one(
                    {'_id': club_info['_id']},
                    {'$set': {'data': Club(server_id, int(club_info['_id'])).dumps()}}
                )

    def join_cup(self):
        if Cup.current_level().level != CUP_PROCESS_PREPARE:
            raise GameException(ConfigErrorMessage.get_error_id("CUP_OUT_OF_APPLY_TIME"))

        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'in_cup': True}}
        )

    def make_cup_protomsg(self):
        doc = MongoCup.db(self.server_id).find_one({'_id': 1})
        if not doc:
            doc = MongoCup.document()
            try:
                MongoCup.db(self.server_id).insert_one(doc)
            except DuplicateKeyError:
                pass

        msg = MessageCup()
        msg.order = doc['order']

        last_champion = doc.get('last_champion', "")
        if last_champion:
            msg.last_champion.MergeFromString(last_champion)

        msg.process = CUP_PROCESS_TABLE[Cup.current_level().level]
        char_doc = MongoCharacter.db(self.server_id).find_one({'_id': self.char_id}, {'in_cup': 1})
        msg.joined = char_doc.get('in_cup', False)

        for i in MongoCupClub.db(self.server_id).find():
            msg_club = msg.clubs.add()
            c = CupClub(self.server_id, i)
            msg_club.MergeFrom(c.make_protomsg())

        for lv in CupLevel.all_match_levels():
            msg_level = msg.levels.add()
            msg_level.process = CUP_PROCESS_TABLE[lv.level]
            msg_level.match_time = lv.start_time.timestamp

            if str(lv.level) in doc['levels']:
                msg_level.club_ids.extend(doc['levels'][str(lv.level)])

        if Cup.current_level().level == CUP_PROCESS_1:
            number_one = doc['levels'][str(CUP_PROCESS_1)][0]
            doc['levels'][str(CUP_PROCESS_2)].remove(number_one)
            number_two = doc['levels'][str(CUP_PROCESS_2)][0]

            doc['levels'][str(CUP_PROCESS_4)].remove(number_one)
            doc['levels'][str(CUP_PROCESS_4)].remove(number_two)

            number_three, number_four = doc['levels'][str(CUP_PROCESS_4)]

            msg.top_four.extend([number_one, number_two, number_three, number_four])

        return msg
