# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       activity
Date Created:   2015-09-21 19:14
Description:

"""

from utils.http import ProtobufResponse

from core.signin import SignIn

from protomsg.activity_pb2 import ActivitySignInResponse


def signin(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    sign_id = request._proto.id

    s = SignIn(server_id, char_id)
    drop = s.sign(sign_id)

    response = ActivitySignInResponse()
    response.ret = 0
    response.drop.MergeFrom(drop)
    return ProtobufResponse(response)
