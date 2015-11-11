# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       character.py
Date Created:   2015-07-29 18:20
Description:

"""
import arrow
from django.conf import settings

from core.mongo import MongoCharacter
from utils.message import MessagePipe

from protomsg.character_pb2 import CharacterNotify, Character as MsgCharacter

from config.settings import (
    CHAR_INIT_DIAMOND,
    CHAR_INIT_GOLD,
    CHAR_INIT_STAFFS,
)


class Character(object):
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    @classmethod
    def create(cls, server_id, char_id, char_name, club_name, club_flag):
        # 这里是club创建完毕后再调用的
        from core.staff import StaffManger
        from core.club import Club

        doc = MongoCharacter.document()
        doc['_id'] = char_id
        doc['name'] = char_name
        doc['create_at'] = arrow.utcnow().timestamp
        doc['club']['name'] = club_name
        doc['club']['flag'] = club_flag
        doc['club']['gold'] = CHAR_INIT_GOLD
        doc['club']['diamond'] = CHAR_INIT_DIAMOND

        MongoCharacter.db(server_id).insert_one(doc)

        sm = StaffManger(server_id, char_id)
        for i in CHAR_INIT_STAFFS:
            sm.add(i, send_notify=False)

        Club(server_id, char_id).set_match_staffs(CHAR_INIT_STAFFS + [0] * 5)

    @classmethod
    def get_recent_login_char_ids(cls, server_id, recent_days=30, other_conditions=None):
        day_limit = arrow.utcnow().replace(days=-recent_days)
        timestamp = day_limit.timestamp

        condition = {'last_login': {'$gte': timestamp}}
        if other_conditions:
            condition = [condition]
            condition.extend(other_conditions)
            condition = {'$and': condition}

        doc = MongoCharacter.db(server_id).find(condition)
        return (d['_id'] for d in doc)

    @property
    def create_days(self):
        # 从创建到现在是第几天。 从1开始
        doc = MongoCharacter.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'create_at': 1}
        )

        create_at = arrow.get(doc['create_at']).to(settings.TIME_ZONE)
        now = arrow.utcnow().to(settings.TIME_ZONE)
        days = (now.date() - create_at.date()).days
        return days + 1

    def set_login(self):
        from django.db.models import F
        from apps.character.models import Character as ModelCharacter
        from core.league import LeagueGame

        now = arrow.utcnow()
        ModelCharacter.objects.filter(id=self.char_id).update(
            last_login=now.format("YYYY-MM-DD HH:mm:ssZ"),
            login_times=F('login_times') + 1,
        )
        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'last_login': now.timestamp}}
        )

        # 联赛只匹配最近一段时间登录的帐号，如果一个帐号很久没登录，那么他将不在联赛里
        # 当他再次登录的时候，这里要检测一下
        LeagueGame.join_already_started_league(self.server_id, self.char_id, send_notify=False)

    def make_protomsg(self, **kwargs):
        if kwargs:
            char = kwargs
        else:
            char = MongoCharacter.db(self.server_id).find_one(
                {'_id': self.char_id},
                {'name': 1}
            )

        msg = MsgCharacter()
        msg.id = str(self.char_id)
        msg.name = char['name']
        # TODO
        msg.avatar = ""
        msg.gender = 1
        msg.age = 19
        msg.profession = 1
        msg.des = u"哈哈哈哈"

        return msg

    def send_notify(self, **kwargs):
        notify = CharacterNotify()
        notify.char.MergeFrom(self.make_protomsg(**kwargs))

        MessagePipe(self.char_id).put(msg=notify)
