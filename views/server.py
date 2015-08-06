# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       server
Date Created:   2015-07-02 18:20
Description:

"""
from utils.http import ProtobufResponse

from dianjing.exception import GameException

from apps.server.models import Server
from apps.character.models import Character

from core.signals import game_start_signal

from config import ConfigErrorMessage

from protomsg.server_pb2 import GetServerListResponse, StartGameResponse
from protomsg.common_pb2 import OPT_OK, OPT_CREATE_CHAR, OPT_CREATE_CLUB

def get_server_list(request):
    servers = Server.opened_servers()
    response = GetServerListResponse()
    response.ret = 0
    for server in servers:
        s = response.servers.add()
        s.id = server.id
        s.name = server.name
        s.status = server.status

    return ProtobufResponse(response)


def start_game(request):
    req = request._proto

    session = request._game_session
    account_id = session.account_id
    server_id = req.server_id

    if not Server.objects.filter(id=server_id).exists():
        raise GameException( ConfigErrorMessage.get_error_id("BAD_MESSAGE") )

    response = StartGameResponse()
    response.ret = 0

    session.server_id = server_id

    try:
        char = Character.objects.get(account_id=account_id, server_id=server_id)
    except Character.DoesNotExist:
        response.next = OPT_CREATE_CHAR
        response.session = session.serialize()
        return ProtobufResponse(response)

    char_id = char.id
    session.char_id = char_id

    if not char.club_name:
        response.next = OPT_CREATE_CLUB
        response.session = session.serialize()
        return ProtobufResponse(response)

    game_start_signal.send(
        sender=None,
        server_id=server_id,
        char_id=char_id,
    )

    response.next = OPT_OK
    response.session = session.serialize()
    return ProtobufResponse(response)

