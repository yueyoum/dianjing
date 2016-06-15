# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       store
Date Created:   2016-05-23 17-17
Description:

"""

from utils.http import ProtobufResponse

from core.store import Store
from protomsg.store_pb2 import (
    StoreBuyResponse,
    StoreAutoRefreshResponse,
    StoreRefreshResponse
)

def buy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    tp = request._proto.tp
    goods_id = request._proto.goods_id

    s = Store(server_id, char_id)
    drop =  s.buy(tp, goods_id)

    response = StoreBuyResponse()
    response.ret = 0
    response.drop.MergeFrom(drop.make_protomsg())
    return ProtobufResponse(response)

def refresh(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    tp = request._proto.tp

    s = Store(server_id, char_id)
    s.refresh(tp)

    response = StoreRefreshResponse()
    response.ret = 0
    return ProtobufResponse(response)


def auto_refresh(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    tp = request._proto.tp

    s = Store(server_id, char_id)
    s.auto_refresh(tp)

    response = StoreAutoRefreshResponse()
    response.ret = 0
    return ProtobufResponse(response)
