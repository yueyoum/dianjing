# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       ladder
Date Created:   2015-08-19 14:13
Description:

"""

from utils.http import ProtobufResponse

from core.ladder import Ladder

from protomsg.ladder_pb2 import LadderRefreshResponse, LadderMatchResponse

def refresh(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    Ladder(server_id, char_id).make_refresh()

    response = LadderRefreshResponse()
    response.ret = 0
    return ProtobufResponse(response)

def match(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    target_id = request._proto.id

    ladder = Ladder(server_id, char_id)
    msg = ladder.match(target_id)

    response = LadderMatchResponse()
    response.ret = 0
    response.match.MergeFrom(msg)
    return ProtobufResponse(response)