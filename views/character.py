# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       character
Date Created:   2015-07-02 18:26
Description:

"""


from django.db import IntegrityError
from dianjing.exception import GameException
from apps.character.models import Character
from utils.http import ProtobufResponse
from utils.message import MessagePipe

from core.signals import char_created_signal

from protomsg.character_pb2 import CreateCharacterResponse, CharacterNotify
from protomsg.common_pb2 import OPT_CREATE_CLUB

from config import ConfigErrorMessage



CHAR_NAME_MAX_LENGTH = 7

def create(request):
    req = request._proto
    name = req.name

    if not name:
        raise GameException( ConfigErrorMessage.get_error_id("BAD_MESSAGE") )
    if len(name) > CHAR_NAME_MAX_LENGTH:
        raise GameException( ConfigErrorMessage.get_error_id("CHAR_NAME_TOO_LONG") )

    session = request._game_session

    account_id = session.account_id
    server_id = session.server_id

    try:
        char = Character.objects.create(
            account_id=account_id,
            server_id=server_id,
            name=name,
        )
    except IntegrityError as e:
        if 'account_id' in e.args[1]:
            raise GameException( ConfigErrorMessage.get_error_id("CHAR_ALREADY_CREATED") )
        raise GameException( ConfigErrorMessage.get_error_id("CHAR_NAME_TAKEN") )

    char_created_signal.send(
        sender=None,
        char_id=char.id,
        char_name=name
    )

    notify = CharacterNotify()
    notify.char.id = char.id
    notify.char.name = name

    MessagePipe(char.id).put(msg=notify)

    session.char_id = char.id

    response = CreateCharacterResponse()
    response.ret = 0
    response.next = OPT_CREATE_CLUB
    response.session = session.serialize()

    return ProtobufResponse(response)

