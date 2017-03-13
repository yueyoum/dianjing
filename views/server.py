# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       server
Date Created:   2015-07-02 18:20
Description:

"""
import base64
from utils.http import ProtobufResponse

from dianjing.exception import GameException

from apps.server.models import Server
from apps.account.models import AccountLoginLog
from apps.character.models import Character

from core.signals import account_login_signal, game_start_signal

from config import ConfigErrorMessage

from protomsg.server_pb2 import GetServerListResponse, StartGameResponse
from protomsg.common_pb2 import OPT_OK, OPT_CREATE_CLUB


def get_server_list(request):
    account_id = request._game_session.account_id

    servers = Server.opened_servers()
    response = GetServerListResponse()
    response.ret = 0

    recommend_id = 0
    max_id = 0

    for server in servers:
        s = response.servers.add()
        s.id = server.id
        s.name = server.name
        s.status = server.status
        s.is_new = server.is_new

        if server.recommend:
            recommend_id = server.id

        if server.id > max_id:
            max_id = server.id

    if not recommend_id:
        recommend_id = max_id

    response.recommend_id = recommend_id
    recent_server_ids = AccountLoginLog.get_account_recent_server_ids(account_id)
    response.recent_ids.extend(recent_server_ids)
    return ProtobufResponse(response)


def start_game(request):
    req = request._proto

    session = request._game_session
    account_id = session.account_id
    server_id = req.server_id

    if not Server.objects.filter(id=server_id).exists():
        raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

    ip = request.META.get("REMOTE_ADDR")
    if not ip:
        ip = ""

    account_login_signal.send(
        sender=None,
        account_id=account_id,
        ip=ip,
        to_server_id=server_id,
    )

    response = StartGameResponse()
    response.ret = 0

    session.server_id = server_id

    try:
        char = Character.objects.get(account_id=account_id, server_id=server_id)
    except Character.DoesNotExist:
        response.next = OPT_CREATE_CLUB
        response.session = session.serialize()
        return ProtobufResponse(response)

    char_id = char.id
    session.char_id = char_id

    game_start_signal.send(
        sender=None,
        server_id=server_id,
        char_id=char_id,
    )

    response.next = OPT_OK
    response.session = session.serialize()

    print
    print "NEW SESSION (base64 encoded)"
    print base64.b64encode(response.session)
    print

    return ProtobufResponse(response)
