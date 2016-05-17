# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       territory
Date Created:   2016-05-17 16-03
Description:

"""

from utils.http import ProtobufResponse

from core.territory import Territory

from protomsg.territory_pb2 import (
    TerritoryTrainingGetRewardResponse,
    TerritoryTrainingPrepareResponse,
    TerritoryTrainingStartResponse,
)


def prepare(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    building_id = request._proto.building_id
    slot_id = request._proto.slot_id
    staff_id = request._proto.staff_id
    hour = request._proto.hour

    t = Territory(server_id, char_id)
    slot = t.training_prepare(building_id, slot_id, staff_id, hour)

    response = TerritoryTrainingPrepareResponse()
    response.ret = 0
    response.exp = slot.reward_building_exp()
    response.product_id =slot.product_id
    response.product_amount = slot.reward_product_amount()
    response.key = slot.key

    return ProtobufResponse(response)


def start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    key = request._proto.key

    t = Territory(server_id, char_id)
    t.training_star(key)

    response = TerritoryTrainingStartResponse()
    response.ret = 0
    return ProtobufResponse(response)
