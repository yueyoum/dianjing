# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       purchase
Date Created:   2016-08-03 17:19
Description:

"""
from django.http import HttpResponse

from utils.http import ProtobufResponse

from core.purchase import Purchase, platform_callback_1sdk
from protomsg.purchase_pb2 import PurchasePrepareResponse, PurchaseVerifyResponse, PurchaseGetFirstRewardResponse


def prepare(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    platform = request._proto.platform
    goods_id = request._proto.goods_id

    p = Purchase(server_id, char_id)
    order_id = p.prepare(platform, goods_id)

    response = PurchasePrepareResponse()
    response.ret = 0
    response.order_id = order_id
    return ProtobufResponse(response)


def verify(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    order_id = request._proto.order_id
    param = request._proto.param

    p = Purchase(server_id, char_id)
    goods_id, status = p.verify(order_id, param)

    response = PurchaseVerifyResponse()
    response.ret = 0
    response.status = status
    response.goods_id = goods_id
    return ProtobufResponse(response)


def get_first_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    p = Purchase(server_id, char_id)
    drop = p.get_first_reward()

    response = PurchaseGetFirstRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(drop.make_protomsg())
    return ProtobufResponse(response)


def callback_1sdk(request):
    content = platform_callback_1sdk(request.GET)
    return HttpResponse(content=content)
