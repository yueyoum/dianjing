# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       core
Date Created:   2015-04-30 15:47
Description:

"""

from apps.character.models import Character as ModelCharacter

from utils.message import MessagePipe

from protomsg.character_pb2 import CharacterNotify

class CharacterManager(object):
    def __init__(self, char_id):
        self.char_id = char_id

    def send_notify(self):
        char = ModelCharacter.objects.get(id=self.char_id)

        msg = CharacterNotify()
        msg.char.id = char.id
        msg.char.name = char.name

        MessagePipe(self.char_id).put(msg)


