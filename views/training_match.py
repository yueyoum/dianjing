# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training_match
Date Created:   2015-12-08 18:36
Description:

"""

from utils.http import ProtobufResponse

from core.training_match import TrainingMatch

from protomsg.training_match_pb2 import TrainingMatchGetAdditionalRewardResponse, TrainingMatchStartResponse


def start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    index = request._proto.club_index

    tm = TrainingMatch(server_id, char_id)
    msg, drop = tm.start(index)

    response = TrainingMatchStartResponse()
    response.ret = 0
    response.match.MergeFrom(msg)
    response.drop.MergeFrom(drop)

    return ProtobufResponse(response)


def get_additional_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    index = request._proto.club_index

    tm = TrainingMatch(server_id, char_id)
    drop = tm.get_additional_reward(index)

    response = TrainingMatchGetAdditionalRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(drop)

    return ProtobufResponse(response)
