# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       character.py
Date Created:   2015-07-29 18:20
Description:

"""

from core.db import MongoDB
from core.mongo import Document
from utils.message import MessagePipe

from protomsg.character_pb2 import CharacterNotify, Character as MsgCharacter


class Character(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = MongoDB.get(server_id)


    @classmethod
    def create(cls, server_id, char_id, char_name, club_name, club_flag):
        doc = Document.get("character")
        doc['_id'] = char_id
        doc['name'] = char_name
        doc['club']['name'] = club_name
        doc['club']['flag'] = club_flag
        doc['club']['gold'] = 100000

        mongo = MongoDB.get(server_id)
        mongo.character.insert_one(doc)


    def make_protomsg(self, **kwargs):
        if kwargs:
            char = kwargs
        else:
            char = self.mongo.character.find_one(
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
