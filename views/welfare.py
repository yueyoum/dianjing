# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       welfare
Date Created:   2016-06-29 10-11
Description:

"""

from utils.http import ProtobufResponse

from core.welfare import Welfare

from protomsg.welfare_pb2 import (
    WelfareEnergyRewardGetResponse,
    WelfareLevelRewardGetResponse,
    WelfareNewPlayerGetResponse,
    WelfareSignInResponse,
)


def signin(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    w = Welfare(server_id, char_id)
    drop = w.signin()

    response = WelfareSignInResponse()
    response.ret = 0
    response.drop.MergeFrom(drop.make_protomsg())
    return ProtobufResponse(response)


def new_player_get(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    _id = request._proto.id

    w = Welfare(server_id, char_id)
    drop = w.new_player_get(_id)

    response = WelfareNewPlayerGetResponse()
    response.ret = 0
    response.drop.MergeFrom(drop.make_protomsg())
    return ProtobufResponse(response)


def level_reward_get(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    _id = request._proto.id

    w = Welfare(server_id, char_id)
    drop = w.level_reward_get(_id)

    response = WelfareLevelRewardGetResponse()
    response.ret = 0
    response.drop.MergeFrom(drop.make_protomsg())
    return ProtobufResponse(response)


def energy_reward_get(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    w = Welfare(server_id, char_id)
    drop = w.energy_reward_get()

    response = WelfareEnergyRewardGetResponse()
    response.ret = 0
    response.drop.MergeFrom(drop.make_protomsg())
    return ProtobufResponse(response)
