# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training
Date Created:   2015-07-21 16:25
Description:

"""

from core.training import TrainingExp, TrainingProperty, TrainingBroadcast, TrainingShop, TrainingSponsor

from utils.http import ProtobufResponse

from protomsg.training_pb2 import (
    TrainingExpStartResponse,
    TrainingExpCancelResponse,
    TrainingExpSpeedupResponse,
    TrainingExpGetRewardResponse,

    TrainingPropertyStartResponse,
    TrainingPropertyCancelResponse,
    TrainingPropertySpeedupResponse,
    TrainingPropertyGetRewardResponse,

    TrainingBroadcastStartResponse,
    TrainingBroadcastCancelResponse,
    TrainingBroadcastSpeedupResponse,
    TrainingBroadcastGetRewardResponse,
    TrainingBroadcastDetailResponse,

    TrainingShopStartResponse,

    TrainingSponsorStartResponse,
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


def property_start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id
    training_id = request._proto.training_id

    tp = TrainingProperty(server_id, char_id)
    tp.start(staff_id, training_id)

    response = TrainingPropertyStartResponse()
    response.ret = 0
    return ProtobufResponse(response)


def property_cancel(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id
    slot_id = request._proto.slot_id

    tp = TrainingProperty(server_id, char_id)
    tp.cancel(staff_id, slot_id)

    response = TrainingPropertyCancelResponse()
    response.ret = 0
    return ProtobufResponse(response)


def property_speedup(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id
    slot_id = request._proto.slot_id

    tp = TrainingProperty(server_id, char_id)
    tp.speedup(staff_id, slot_id)

    response = TrainingPropertySpeedupResponse()
    response.ret = 0
    return ProtobufResponse(response)


def property_get_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id
    slot_id = request._proto.slot_id

    tp = TrainingProperty(server_id, char_id)
    p = tp.get_reward(staff_id, slot_id)

    response = TrainingPropertyGetRewardResponse()
    response.ret = 0
    response.property.MergeFrom(p)
    return ProtobufResponse(response)


def broadcast_start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id
    staff_id = request._proto.staff_id

    tb = TrainingBroadcast(server_id, char_id)
    tb.start(slot_id, staff_id)

    response = TrainingBroadcastStartResponse()
    response.ret = 0
    return ProtobufResponse(response)


def broadcast_detail(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id

    tb = TrainingBroadcast(server_id, char_id)
    drop = tb.get_drop(slot_id)

    response = TrainingBroadcastDetailResponse()
    response.ret = 0
    response.drop.MergeFrom(drop.make_protomsg())
    return ProtobufResponse(response)


def broadcast_cancel(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id

    tb = TrainingBroadcast(server_id, char_id)
    drop = tb.cancel(slot_id)

    response = TrainingBroadcastCancelResponse()
    response.ret = 0
    response.drop.MergeFrom(drop.make_protomsg())
    return ProtobufResponse(response)


def broadcast_speedup(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id

    tb = TrainingBroadcast(server_id, char_id)
    tb.speedup(slot_id)

    response = TrainingBroadcastSpeedupResponse()
    response.ret = 0
    return ProtobufResponse(response)


def broadcast_get_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id

    tb = TrainingBroadcast(server_id, char_id)
    drop = tb.get_reward(slot_id)

    response = TrainingBroadcastGetRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(drop.make_protomsg())
    return ProtobufResponse(response)


def shop_start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    shop_id = request._proto.slot_id
    staff_id = request._proto.staff_id

    ts = TrainingShop(server_id, char_id)
    ts.start(shop_id, staff_id)

    response = TrainingShopStartResponse()
    response.ret = 0
    return ProtobufResponse(response)


def sponsor_start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    sponsor_id = request._proto.id

    ts = TrainingSponsor(server_id, char_id)
    ts.start(sponsor_id)

    response = TrainingPropertyStartResponse()
    response.ret = 0
    return ProtobufResponse(response)
