# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       purchase
Date Created:   2016-08-03 17:19
Description:

"""
from django.http import HttpResponse

from utils.http import ProtobufResponse

from core.purchase import Purchase, platform_callback
from protomsg.purchase_pb2 import PurchasePrepareResponse, PurchaseVerifyResponse

def prepare(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    goods_id = request._proto.goods_id
    goods_amount = request._proto.goods_amount

    p = Purchase(server_id, char_id)
    receipt = p.prepare(goods_id, goods_amount)

    response = PurchasePrepareResponse()
    response.ret = 0
    response.receipt = receipt
    return ProtobufResponse(response)


def verify(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    receipt = request._proto.receipt

    p = Purchase(server_id, char_id)
    obj, status = p.verify(receipt)

    response = PurchaseVerifyResponse()
    response.ret = 0
    response.status = status
    response.goods_id = obj.goods_id
    response.goods_amount = obj.goods_amount
    return ProtobufResponse(response)


def callback(request):
    platform_callback(request.GET)

    return HttpResponse('')