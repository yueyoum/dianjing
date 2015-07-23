# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       game
Date Created:   2015-04-30 15:23
Description:

"""

import arrow

from core.signals import game_start_signal
from core.club import Club
from core.staff import StaffRecruit, StaffManger
from core.challenge import Challenge
from core.building import BuildingManager
from core.training import Training
from core.league import League

from core.db import get_mongo_db


from utils.message import MessagePipe
from protomsg.common_pb2 import UTCNotify
from protomsg.character_pb2 import CharacterNotify


def start(server_id, char_id, **kwargs):
    MessagePipe(char_id).clean()

    msg = UTCNotify()
    msg.timestamp = arrow.utcnow().timestamp
    MessagePipe(char_id).put(msg=msg)

    mongo = get_mongo_db(server_id)
    char = mongo.character.find_one({'_id': char_id}, {'name': 1})

    notify = CharacterNotify()
    notify.char.id = char_id
    notify.char.name = char['name']
    MessagePipe(char_id).put(msg=notify)

    Club(server_id, char_id).send_notify()
    StaffRecruit(server_id, char_id).send_notify()
    StaffManger(server_id, char_id).send_notify()

    Challenge(server_id, char_id).send_notify()
    BuildingManager(server_id, char_id).send_notify()
    Training(server_id, char_id).send_notify()
    League(server_id, char_id).send_notify()


game_start_signal.connect(
    start,
    dispatch_uid='signals.game.start'
)
