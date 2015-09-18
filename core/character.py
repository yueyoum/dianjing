# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       character.py
Date Created:   2015-07-29 18:20
Description:

"""
import arrow
from core.mongo import MongoCharacter
from utils.message import MessagePipe

from protomsg.character_pb2 import CharacterNotify, Character as MsgCharacter


class Character(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id


    @classmethod
    def create(cls, server_id, char_id, char_name, club_name, club_flag):
        from core.staff import StaffManger
        from core.club import Club
        from core.training import TrainingBag

        doc = MongoCharacter.document()
        doc['_id'] = char_id
        doc['name'] = char_name
        doc['club']['name'] = club_name
        doc['club']['flag'] = club_flag
        doc['club']['gold'] = 100000

        MongoCharacter.db(server_id).insert_one(doc)

        sm = StaffManger(server_id, char_id)
        staff_ids = [2,3,4,5,6]
        for i in staff_ids:
            sm.add(i, send_notify=False)

        Club(server_id, char_id).set_match_staffs(staff_ids + [0] * 5)

        TrainingBag(server_id, char_id).add_from_raw_training(1, send_notify=False)

    def set_login(self):
        from django.db.models import F
        from apps.character.models import Character as ModelCharacter

        ModelCharacter.objects.filter(id=self.char_id).update(login_times=F('login_times')+1)
        now = arrow.utcnow().timestamp
        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'last_login': now}}
        )


    def make_protomsg(self, **kwargs):
        if kwargs:
            char = kwargs
        else:
            char = MongoCharacter.db(self.server_id).find_one(
                {'_id': self.char_id},
                # TODO field
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
