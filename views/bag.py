# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       bag
Date Created:   2016-03-10 15-14
Description:

"""

from utils.http import ProtobufResponse
from core.bag import Bag

from protomsg.bag_pb2 import (
    BagEquipmentLevelupResponse,
    BagEquipmentOnResponse,
    BagItemDestroyResponse,
    BagItemMergeResponse,
    BagItemUseResponse,
)


def use(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id

    bag = Bag(server_id, char_id)
    result = bag.use(slot_id)

    response = BagItemUseResponse()
    response.ret = 0
    for item_id, amount in result:
        response_result = response.results.add()
        response_result.item_id = item_id
        response_result.amount = amount

    return ProtobufResponse(response)


def merge(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id

    bag = Bag(server_id, char_id)
    bag.merge(slot_id)

    response = BagItemMergeResponse()
    response.ret = 0
    return ProtobufResponse(response)


def destroy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id

    bag = Bag(server_id, char_id)
    bag.destroy(slot_id)

    response = BagItemDestroyResponse()
    response.ret = 0
    return ProtobufResponse(response)


def equipment_level_up(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id

    bag = Bag(server_id, char_id)
    bag.destroy(slot_id)

    response = BagEquipmentLevelupResponse()
    response.ret = 0
    return ProtobufResponse(response)
