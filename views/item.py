# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       item
Date Created:   2016-01-08 10-20
Description:

"""

from utils.http import ProtobufResponse

from core.item import ItemManager

from protomsg.item_pb2 import ItemSellResponse, ItemUseResponse


def sell(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    item_id = request._proto.id
    amount = request._proto.amount

    im = ItemManager(server_id, char_id)
    im.sell(item_id, amount)

    response = ItemSellResponse()
    response.ret = 0
    return ProtobufResponse(response)

def use(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    item_id = request._proto.id
    amount = request._proto.amount

    im = ItemManager(server_id, char_id)
    drop = im.use(item_id, amount)

    response = ItemUseResponse()
    response.ret = 0
    response.drop.MergeFrom(drop.make_protomsg())
    return ProtobufResponse(response)