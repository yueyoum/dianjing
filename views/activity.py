# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       activity
Date Created:   2015-09-21 19:14
Description:

"""

from utils.http import ProtobufResponse

from core.activity.signin import SignIn
from core.activity.login_reward import ActivityLoginReward

from protomsg.activity_pb2 import ActivitySignInResponse, ActivityLoginRewardResponse


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

def get_login_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    _id = request._proto.id

    a = ActivityLoginReward(server_id, char_id)
    drop = a.get_reward(_id)

    response = ActivityLoginRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(drop)
    return ProtobufResponse(response)
