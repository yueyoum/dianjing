# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training
Date Created:   2015-07-21 16:25
Description:

"""

from core.training import TrainingExp

from utils.http import ProtobufResponse

from protomsg.training_pb2 import (
    TrainingExpStartResponse,
    TrainingExpCancelResponse,
    TrainingExpSpeedupResponse,
    TrainingExpGetRewardResponse,
)


def exp_start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id
    staff_id = request._proto.staff_id

    te = TrainingExp(server_id, char_id)
    te.start(slot_id, staff_id)

    response = TrainingExpStartResponse()
    response.ret = 0
    return ProtobufResponse(response)


def exp_cancel(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id

    te = TrainingExp(server_id, char_id)
    p = te.cancel(slot_id)

    response = TrainingExpCancelResponse()
    response.ret = 0
    response.property.MergeFrom(p)
    return ProtobufResponse(response)


def exp_speedup(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id

    te = TrainingExp(server_id, char_id)
    te.speedup(slot_id)

    response = TrainingExpSpeedupResponse()
    response.ret = 0
    return ProtobufResponse(response)


def exp_get_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id

    te = TrainingExp(server_id, char_id)
    p = te.get_reward(slot_id)

    response = TrainingExpGetRewardResponse()
    response.ret = 0
    response.property.MergeFrom(p)
    return ProtobufResponse(response)
