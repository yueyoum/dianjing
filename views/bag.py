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
    BagEquipmentDestroyResponse,
    BagItemDestroyResponse,
    BagItemMergeResponse,
    BagItemUseResponse,
)


def item_use(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id
    amount = request._proto.amount

    bag = Bag(server_id, char_id)
    resource_classified = bag.item_use(slot_id, amount)

    response = BagItemUseResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())

    return ProtobufResponse(response)


def item_merge(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id

    bag = Bag(server_id, char_id)
    resource_classified = bag.item_merge(slot_id)

    response = BagItemMergeResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())
    return ProtobufResponse(response)


def item_destroy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id

    bag = Bag(server_id, char_id)
    resource_classified = bag.item_destroy(slot_id)

    response = BagItemDestroyResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())
    return ProtobufResponse(response)


def equipment_destroy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id
    use_sycee = request._proto.use_sycee

    bag = Bag(server_id, char_id)
    resource_classified = bag.equipment_destroy(slot_id, use_sycee)

    response = BagEquipmentDestroyResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())

    return ProtobufResponse(response)

def equipment_level_up(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id
    single = request._proto.single

    if single:
        times = 1
    else:
        times = 5

    bag = Bag(server_id, char_id)
    error_code, levelup, equip = bag.equipment_level_up(slot_id, times)

    response = BagEquipmentLevelupResponse()
    response.ret = error_code
    response.equipment.MergeFrom(equip.make_protomsg())
    response.levelup = levelup
    return ProtobufResponse(response)
