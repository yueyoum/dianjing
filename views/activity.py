# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       activity
Date Created:   2016-08-05 18:04
Description:

"""

from utils.http import ProtobufResponse

from core.activity import (
    ActivityNewPlayer,
    ActivityChallenge,
    ActivityOnlineTime,
    ActivityPurchaseDaily,
    ActivityPurchaseContinues,
    ActivityLevelGrowing,
)

from protomsg.activity_pb2 import (
    ActivityNewPlayerDailyBuyResponse,
    ActivityNewPlayerGetRewardResponse,
    ActivityChallengeGetRewardResponse,
    ActivityOnlineTimeGetRewardResponse,
    ActivityLevelGrowingGetRewardResponse,
    ActivityPurchaseContinuesGetRewardResponse,
    ActivityPurchaseDailyGetRewardResponse,
    ActivityLevelGrowingJoinResponse,
)

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

def online_time_get_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    at = ActivityOnlineTime(server_id, char_id)
    rc = at.get_reward()

    response = ActivityOnlineTimeGetRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(rc.make_protomsg())
    return ProtobufResponse(response)


def activity_challenge_get_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    _id = request._proto.id

    ac = ActivityChallenge(server_id, char_id)
    rc = ac.get_reward(_id)

    response = ActivityChallengeGetRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(rc.make_protomsg())
    return ProtobufResponse(response)


def purchase_daily_get_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    p = ActivityPurchaseDaily(server_id, char_id)
    rc = p.get_reward()

    response = ActivityPurchaseDailyGetRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(rc.make_protomsg())
    return ProtobufResponse(response)

def purchase_continues_get_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    _id = request._proto.id

    p = ActivityPurchaseContinues(server_id, char_id)
    rc = p.get_reward(_id)

    response = ActivityPurchaseContinuesGetRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(rc.make_protomsg())
    return ProtobufResponse(response)

def level_growing_join(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id


    ActivityLevelGrowing(server_id, char_id).join()

    response = ActivityLevelGrowingJoinResponse()
    response.ret = 0
    return ProtobufResponse(response)

def level_growing_get_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    _id = request._proto.id

    l = ActivityLevelGrowing(server_id, char_id)
    rc = l.get_reward(_id)

    response = ActivityLevelGrowingGetRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(rc.make_protomsg())
    return ProtobufResponse(response)