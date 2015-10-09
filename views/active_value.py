# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       active_value
Date Created:   2015-10-09 17:46
Description:

"""

from utils.http import ProtobufResponse
from core.active_value import ActiveValue

from protomsg.active_value_pb2 import ActiveValueGetRewardResponse


def get_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    reward_id = request._proto.id

    av = ActiveValue(server_id, char_id)
    drop = av.get_reward(reward_id)

    response = ActiveValueGetRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(drop)

    return ProtobufResponse(response)
