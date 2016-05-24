# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       vip
Date Created:   2016-05-24 15-31
Description:

"""

from utils.http import ProtobufResponse

from core.vip import VIP

from protomsg.vip_pb2 import VIPBuyRewardResponse


def buy_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    vip_level = request._proto.vip

    v = VIP(server_id, char_id)
    rc = v.buy_reward(vip_level)

    response = VIPBuyRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(rc.make_protomsg())

    return ProtobufResponse(response)
