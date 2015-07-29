# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       character.py
Date Created:   2015-07-29 18:20
Description:

"""

from core.db import get_mongo_db
from utils.message import MessagePipe

from protomsg.character_pb2 import CharacterNotify, Character as MsgCharacter


class Character(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = get_mongo_db(server_id)

    def make_protomsg(self):
        char = self.mongo.character.find_one(
            {'_id': self.char_id},
            # TODO field
            {'name': 1}
        )
        msg = MsgCharacter()
        msg.id = self.char_id
        msg.name = char['name']
        # TODO
        msg.avatar = ""
        msg.gender = 1
        msg.age = 19
        msg.profession = 1
        msg.des = "哈哈哈哈"

        return msg

    def send_notify(self):
        notify = CharacterNotify()
        notify.char.MergeFrom(self.make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)
