# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       cup
Date Created:   2015-08-27 17:21
Description:

"""

from utils.http import ProtobufResponse

from core.cup import Cup

from protomsg.cup_pb2 import CupInfomationResponse, CupJoinResponse


def join(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    c = Cup(server_id, char_id)
    c.join_cup()
    msg = c.make_cup_protomsg()

    response = CupJoinResponse()
    response.cup.MergeFrom(msg)

    return ProtobufResponse(response)


def information(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    c = Cup(server_id, char_id)
    msg = c.make_cup_protomsg()

    response = CupInfomationResponse()
    response.cup.MergeFrom(msg)

    return ProtobufResponse(response)

