# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       club
Date Created:   2015-07-08 15:12
Description:

"""

from django.db import IntegrityError

from dianjing.exception import GameException
from apps.character.models import Character as ModelCharacter

from utils.http import ProtobufResponse
from config import ConfigErrorMessage

from core.signals import game_start_signal
from core.character import Character

from protomsg.club_pb2 import (
    CreateClubResponse,
)


def create(request):
    name = request._proto.name
    flag = request._proto.flag

    session = request._game_session
    server_id = session.server_id
    char_id = session.char_id

    char = ModelCharacter.objects.get(id=char_id)
    if char.club_name:
        raise GameException(ConfigErrorMessage.get_error_id("CLUB_ALREADY_CREATED"))

    try:
        char.club_name = name
        char.save()
    except IntegrityError:
        raise GameException(ConfigErrorMessage.get_error_id("CLUB_NAME_TAKEN"))

    Character.create(server_id, char_id, char.name, name, flag)

    game_start_signal.send(
        sender=None,
        server_id=server_id,
        char_id=char_id,
    )

    response = CreateClubResponse()
    response.ret = 0
    response.session = session.serialize()
    return ProtobufResponse(response)

