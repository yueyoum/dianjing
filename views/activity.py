# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       activity
Date Created:   2016-08-05 18:04
Description:

"""

from utils.http import ProtobufResponse

from core.activity import ActivityNewPlayer

from protomsg.activity_pb2 import ActivityNewPlayerDailyBuyResponse, ActivityNewPlayerGetRewardResponse

def newplayer_getreward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    _id = request._proto.id

    ac = ActivityNewPlayer(server_id, char_id)
    rc = ac.get_reward(_id)

    response = ActivityNewPlayerGetRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(rc.make_protomsg())
    return ProtobufResponse(response)

def newplayer_dailybuy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    ac = ActivityNewPlayer(server_id, char_id)
    rc = ac.daily_buy()

    response = ActivityNewPlayerDailyBuyResponse()
    response.ret = 0
    response.drop.MergeFrom(rc.make_protomsg())
    return ProtobufResponse(response)