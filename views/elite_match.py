# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       elite_match
Date Created:   2015-12-10 15:01
Description:

"""

from utils.http import ProtobufResponse

from core.elite_match import EliteMatch

from protomsg.elite_match_pb2 import EliteStartResponse


def start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    match_id = request._proto.match_id

    em = EliteMatch(server_id, char_id)
    msg, drop = em.start(match_id)

    response = EliteStartResponse()
    response.ret = 0
    response.match.MergeFrom(msg)
    response.drop.MergeFrom(drop)

    return ProtobufResponse(response)
