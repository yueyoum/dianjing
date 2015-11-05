# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       shop
Date Created:   2015-11-05 10:26
Description:

"""

from utils.http import ProtobufResponse

from core.shop import ItemShop
from protomsg.shop_pb2 import ItemShopBuyResponse


def item_shop_buy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    item_id = request._proto.id
    amount = request._proto.amount

    ItemShop(server_id, char_id).buy(item_id, amount)

    response = ItemShopBuyResponse()
    response.ret = 0
    return ProtobufResponse(response)
