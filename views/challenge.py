# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2015-07-15 17:43
Description:

"""

from utils.http import ProtobufResponse

from core.challenge import Challenge

from protomsg.challenge_pb2 import ChallengeStartResponse

def start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    c = Challenge(server_id, char_id)
    msg = c.start()

    response = ChallengeStartResponse()
    response.ret = 0
    response.match.MergeFrom(msg)

    return ProtobufResponse(response)
