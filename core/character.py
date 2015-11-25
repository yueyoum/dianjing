# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       character.py
Date Created:   2015-07-29 18:20
Description:

"""
import arrow
from sevencow import Cow, CowException

from django.conf import settings

from dianjing.exception import GameException
from core.mongo import MongoCharacter
from utils.message import MessagePipe

from protomsg.character_pb2 import CharacterNotify, Character as MsgCharacter
from protomsg.common_pb2 import UPLOAD_DONE, UPLOAD_NONE, UPLOAD_VERIFY

from config.settings import (
    CHAR_INIT_DIAMOND,
    CHAR_INIT_GOLD,
    CHAR_INIT_STAFFS,
)

from config import ConfigErrorMessage


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

        Club(server_id, char_id).set_match_staffs(CHAR_INIT_STAFFS + [0] * 5, trig_signal=False)

    @classmethod
    def get_recent_login_char_ids(cls, server_id, recent_days=7, other_conditions=None):
        day_limit = arrow.utcnow().replace(days=-recent_days)
        timestamp = day_limit.timestamp

        condition = {'last_login': {'$gte': timestamp}}
        if other_conditions:
            condition = [condition]
            condition.extend(other_conditions)
            condition = {'$and': condition}

        doc = MongoCharacter.db(server_id).find(condition)
        for d in doc:
            yield d['_id']

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

    def set_avatar(self, url, ok):
        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'avatar_key': url,
                'avatar_ok': ok
            }}
        )

        self.send_notify()

    def make_protomsg(self, **kwargs):
        if kwargs:
            char = kwargs
        else:
            char = MongoCharacter.db(self.server_id).find_one({'_id': self.char_id})

        msg = MsgCharacter()
        msg.id = str(self.char_id)
        msg.name = char['name']

        avatar_key = char.get('avatar_key', "")
        avatar_ok = char.get('avatar_ok', False)

        if not avatar_key:
            msg.avatar = ""
            msg.avatar_status = UPLOAD_NONE
        else:
            msg.avatar = "http://{0}/{1}".format(settings.QINIU_DOMAIN, avatar_key)
            if avatar_ok:
                msg.avatar_status = UPLOAD_DONE
            else:
                msg.avatar_status = UPLOAD_VERIFY

        # TODO
        msg.gender = 1
        msg.age = 19
        msg.profession = 1
        msg.des = u"哈哈哈哈"

        return msg

    def send_notify(self, **kwargs):
        notify = CharacterNotify()
        notify.char.MergeFrom(self.make_protomsg(**kwargs))

        MessagePipe(self.char_id).put(msg=notify)


def save_avatar(server_id, char_id, data):
    from apps.character.models import Character as ModelCharacter

    cow = Cow(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
    bucket = cow.get_bucket(settings.QINIU_BUCKET)

    # 我们上传的图片全部定死是png的
    try:
        ret = bucket.put('x.png', data=data)
    except CowException:
        raise GameException(ConfigErrorMessage.get_error_id("UPLOAD_AVATAR_ERROR"))

    key = ret['key']

    mc = ModelCharacter.objects.get(id=char_id)
    if mc.avatar_key:
        # 清除旧头像
        try:
            bucket.delete(mc.avatar_key)
        except CowException:
            pass

    mc.avatar_key = key
    mc.avatar_ok = False
    mc.save()

    Character(server_id, char_id).set_avatar(key, False)
