# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       territory
Date Created:   2016-05-17 16-03
Description:

"""

from utils.http import ProtobufResponse

from core.territory import Territory, TerritoryStore

from protomsg.territory_pb2 import (
    TerritoryTrainingGetRewardResponse,
    TerritoryTrainingStartResponse,
    TerritoryFriendHelpResponse,
    TerritoryFriendListResponse,
    TerritoryMatchReportResponse,
    TerritoryStoreBuyResponse,
)

def start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    building_id = request._proto.building_id
    slot_id = request._proto.slot_id
    staff_id = request._proto.staff_id
    hour = request._proto.hour

    t = Territory(server_id, char_id)
    t.training_star(building_id, slot_id, staff_id, hour)

    response = TerritoryTrainingStartResponse()
    response.ret = 0
    return ProtobufResponse(response)


def get_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    building_id = request._proto.building_id
    slot_id = request._proto.slot_id

    t = Territory(server_id, char_id)
    resource_classified = t.training_get_reward(building_id, slot_id)

    response = TerritoryTrainingGetRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())
    return ProtobufResponse(response)


def store_buy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    _id = request._proto.id

    t = TerritoryStore(server_id, char_id)
    resource_classified = t.buy(_id)

    response = TerritoryStoreBuyResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())
    return ProtobufResponse(response)
