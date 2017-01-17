# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       purchase
Date Created:   2016-08-03 17:19
Description:

"""
from django.http import HttpResponse

from utils.http import ProtobufResponse

from core.purchase import Purchase, platform_callback_1sdk, platform_callback_stars_cloud
from protomsg.purchase_pb2 import PurchaseVerifyResponse, PurchaseGetFirstRewardResponse
from protomsg.common_pb2 import PLATFORM_1SDK, PLATFORM_IOS


def verify(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    platform = request._proto.platform
    param = request._proto.param

    p = Purchase(server_id, char_id)

    if platform == PLATFORM_IOS:
        goods_id, status = p.verify_ios(param)
    else:
        goods_id, status = p.verify_other(param)

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

def callback_stars_cloud(request):
    content = platform_callback_stars_cloud(request.POST)
    return HttpResponse(content=content)
