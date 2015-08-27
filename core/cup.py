# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       cup
Date Created:   2015-08-26 15:16
Description:

"""

import random
import calendar
import arrow

from pymongo.errors import DuplicateKeyError

from django.conf import settings

from dianjing.exception import GameException

from core.db import MongoDB
from core.mongo import Document
from core.abstract import AbstractStaff, AbstractClub
from core.club import Club

from utils.functional import make_string_id

from config import ConfigErrorMessage, ConfigNPC

from protomsg import cup_pb2
from protomsg.cup_pb2 import Cup as MessageCup

# 服务器程序内部使用
CUP_PROCESS_APPLY = 1000       # 报名
CUP_PROCESS_PREPARE = 1001     # 预选赛

CUP_PROCESS_32 = 32         # 32强
CUP_PROCESS_16 = 16         # 16强
CUP_PROCESS_8 = 8           # 8强
CUP_PROCESS_4 = 4           # 4强    半决赛
CUP_PROCESS_2 = 2           # 2强    总决赛
CUP_PROCESS_1 = 1           # 结束


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
    def __init__(self, club_data):
        super(CupNpcClub, self).__init__()
        self.id = club_data['_id']
        self.name = club_data['club_name']
        self.manager_name = club_data['manager_name']
        self.flag = club_data['club_flag']


class CupClub(object):
    def __new__(cls, server_id, club_data):
        if club_data['club_name']:
            return CupNpcClub(club_data)

        return Club(server_id, int(club_data['_id']))




class CupLevel(object):
    def __init__(self, year, month, lv):
        self.level = lv
        self.match_time = 0

        day = 1
        hour = 0
        if lv == CUP_PROCESS_APPLY:
            pass
        elif lv == CUP_PROCESS_PREPARE:
            day = 4
        elif lv == CUP_PROCESS_32:
            day = 5
        elif lv == CUP_PROCESS_16:
            day = 10
        elif lv == CUP_PROCESS_8:
            day = 15
        elif lv == CUP_PROCESS_4:
            day = 20
        elif lv == CUP_PROCESS_2:
            day = 25
        elif lv == CUP_PROCESS_1:
            day = calendar.monthrange(year, month)[1]
            hour = 22

        self.start_time = arrow.Arrow(year, month, day, hour, 0, 0, tzinfo=settings.TIME_ZONE)


    @classmethod
    def current_level(cls):
        now = arrow.utcnow().to(settings.TIME_ZONE)
        current_day = now.day
        last_day_of_this_month = calendar.monthrange(now.year, now.month)


        if current_day < 4:
            # 1 ~ 3
            level = CUP_PROCESS_APPLY
        elif current_day < 5:
            # 4
            level = CUP_PROCESS_PREPARE
        elif current_day < 10:
            # 5 ~ 9
            level = CUP_PROCESS_32
        elif current_day < 15:
            # 10 ~ 14
            level = CUP_PROCESS_16
        elif current_day < 20:
            # 15 ~ 20
            level = CUP_PROCESS_8
        elif current_day < 25:
            # 20 ~ 24
            level = CUP_PROCESS_4
        elif current_day < last_day_of_this_month:
            # 25 ~ last_day_of_this_month - 1
            level = CUP_PROCESS_2
        else:
            # last_day_of_this_month
            if now.hour <= 22:
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
        self.mongo = MongoDB.get(server_id)


    @staticmethod
    def new(server_id):
        # 开始一场新的
        db = MongoDB.get(1)
        db.cup_club.drop()
        db.cup.update_one(
            {'_id': 1},
            {
                '$set': {
                    'levels': {}
                },
                '$inc': {
                    'order': 1
                }
            },
            upsert=True,
        )


    @staticmethod
    def prepare(server_id):
        # 预选赛， 选出32强

        db = MongoDB.get(server_id)


        # TODO real rule
        chars = db.character.find({'in_cup': 1}, {'_id': 1})
        char_ids = [c['_id'] for c in chars]
        if len(char_ids) >= 32:
            char_ids = random.sample(char_ids, 16)

        need_npc_amount = 32 - len(char_ids)
        npcs = ConfigNPC.random_npcs(need_npc_amount, 1)

        docs = []
        for i in char_ids:
            doc = Document.get("cup.club")
            doc['_id'] = str(i)
            doc['staffs'] = []

            docs.append(doc)

        for n in npcs:
            doc = Document.get("cup.club")
            doc['_id'] = make_string_id()
            doc['club_name'] = n['club_name']
            doc['manager_name'] = n['manager_name']
            doc['club_flag'] = n['club_flag']
            doc['staffs'] = n['staffs']

            docs.append(doc)

        db.cup_club.insert_many(docs)
        db.cup.update_one(
            {'_id': 1},
            {'$set': {'levels.{0}'.format(CUP_PROCESS_32): [d['_id'] for d in docs]}}
        )


    @staticmethod
    def match(server_id):
        db = MongoDB.get(server_id)

        all_passed_match_levels = CupLevel.all_passed_match_levels()

        cup_doc = db.cup.find_one({'_id': 1})

        for i in range(1, len(all_passed_match_levels)):
            lv = all_passed_match_levels[i].level
            if str(lv) not in cup_doc['levels']:
                club_ids = cup_doc['levels'][str(all_passed_match_levels[i-1].level)]
                # TODO real match

                next_level_club_ids = []
                for i in range(0, len(club_ids)-1, 2):
                    next_level_club_ids.append( random.choice([club_ids[i], club_ids[i+1]]) )

                cup_doc['levels'][str(lv)] = next_level_club_ids
                db.cup.update_one(
                    {'_id': 1},
                    {'$set': {'levels.{0}'.format(lv): next_level_club_ids}}
                )


    @staticmethod
    def current_level():
        return CupLevel.current_level()


    def join_cup(self):
        if Cup.current_level().level != CUP_PROCESS_PREPARE:
            raise GameException(ConfigErrorMessage.get_error_id("CUP_OUT_OF_APPLY_TIME"))

        self.mongo.character.update_one(
            {'_id': self.char_id},
            {'$set': {'in_cup': True}}
        )


    def make_cup_protomsg(self):
        cup_doc = self.mongo.cup.find_one({'_id': 1})
        if not cup_doc:
            cup_doc = Document.get("cup")
            try:
                self.mongo.cup.insert_one(cup_doc)
            except DuplicateKeyError:
                pass

        msg = MessageCup()
        msg.order = cup_doc['order']

        last_champion = cup_doc.get('last_champion', "")
        if last_champion:
            msg.last_champion.MergeFromString(last_champion)

        msg.process = CUP_PROCESS_TABLE[Cup.current_level().level]
        char = self.mongo.character.find_one({'_id': self.char_id}, {'in_cup': 1})
        msg.joined = char.get('in_cup', False)

        for i in self.mongo.cup_club.find():
            msg_club = msg.clubs.add()
            c = CupClub(self.server_id, i)
            msg_club.MergeFrom(c.make_protomsg())

        for lv in CupLevel.all_match_levels():
            msg_level = msg.levels.add()
            msg_level.process = CUP_PROCESS_TABLE[lv.level]
            msg_level.match_time = lv.start_time.timestamp

            if str(lv.level) in cup_doc['levels']:
                msg_level.club_ids.extend(cup_doc['levels'][str(lv.level)])


        if Cup.current_level().level == CUP_PROCESS_1:
            number_one = cup_doc['levels'][str(CUP_PROCESS_1)][0]
            cup_doc['levels'][str(CUP_PROCESS_2)].remove(number_one)
            number_two = cup_doc['levels'][str(CUP_PROCESS_2)][0]

            cup_doc['levels'][str(CUP_PROCESS_4)].remove(number_one)
            cup_doc['levels'][str(CUP_PROCESS_4)].remove(number_two)

            number_three, number_four = cup_doc['levels'][str(CUP_PROCESS_4)]

            msg.top_four.extend([number_one, number_two, number_three, number_four])

        return msg
