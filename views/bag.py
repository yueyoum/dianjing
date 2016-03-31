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
    BagEquipmentLevelupConfirmResponse,
    BagEquipmentDestroyResponse,
    BagItemDestroyResponse,
    BagItemMergeResponse,
    BagItemUseResponse,
)

# TODO package.Drop
from protomsg.package_pb2 import Drop


def item_use(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id

    bag = Bag(server_id, char_id)
    result = bag.item_use(slot_id)

    response = BagItemUseResponse()
    response.ret = 0

    d = Drop()
    for item_id, amount in result:
        d_item = d.items.add()
        d_item.id = item_id
        d_item.amount = amount
        d_item.tp = 100

    response.drop.MergeFrom(d)

    return ProtobufResponse(response)


def item_merge(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id

    bag = Bag(server_id, char_id)
    bag.item_merge(slot_id)

    response = BagItemMergeResponse()
    response.ret = 0
    return ProtobufResponse(response)


def item_destroy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id

    bag = Bag(server_id, char_id)
    bag.item_destroy(slot_id)

    response = BagItemDestroyResponse()
    response.ret = 0
    return ProtobufResponse(response)


def equipment_destroy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id
    use_sycee = request._proto.use_sycee

    bag = Bag(server_id, char_id)
    items = bag.equipment_destroy(slot_id, use_sycee)

    response = BagEquipmentDestroyResponse()
    response.ret = 0
    for a, b in items:
        response_item = response.drop.items.add()
        response_item.id = a
        response_item.amount = b
        response_item.tp = 100

    return ProtobufResponse(response)


def equipment_level_up_preview(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id

    bag = Bag(server_id, char_id)
    msg_equip = bag.equipment_level_up_preview(slot_id)

    response = BagEquipmentLevelupResponse()
    response.ret = 0
    response.equipment.MergeFrom(msg_equip)
    return ProtobufResponse(response)

def equipment_level_up_confirm(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id
    single = request._proto.single

    if single:
        times = 1
    else:
        times = 5

    bag = Bag(server_id, char_id)
    msg_equip = bag.equipment_level_up_confirm(slot_id, times)

    response = BagEquipmentLevelupConfirmResponse()
    response.ret = 0
    response.equipment.MergeFrom(msg_equip)
    return ProtobufResponse(response)
