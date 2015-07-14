# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       game
Date Created:   2015-04-30 15:23
Description:

"""

import arrow

from core.signals import game_start_signal
from core.club import ClubManager
from core.staff import StaffRecruit, StaffManger
from core.db import get_mongo_db


from utils.message import MessagePipe
from protomsg.common_pb2 import UTCNotify
from protomsg.character_pb2 import CharacterNotify


def start(server_id, char_id, **kwargs):
    msg = UTCNotify()
    msg.timestamp = arrow.utcnow().timestamp
    MessagePipe(char_id).put(msg=msg)

    mongo = get_mongo_db(server_id)
    char = mongo.character.find_one({'_id': char_id}, {'name': 1})

    notify = CharacterNotify()
    notify.char.id = char_id
    notify.char.name = char['name']
    MessagePipe(char_id).put(msg=notify)

    ClubManager(server_id, char_id).send_notify()
    StaffRecruit(server_id, char_id).send_notify()
    StaffManger(server_id, char_id).send_notify()


game_start_signal.connect(
    start,
    dispatch_uid='signals.game.start'
)
