# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       purchase
Date Created:   2016-08-03 17:19
Description:

"""
from django.http import HttpResponse
from dianjing.exception import GameException
from utils.http import ProtobufResponse
from config import ConfigErrorMessage

from core.purchase import Purchase, platform_callback_1sdk, platform_callback_stars_cloud
from protomsg.purchase_pb2 import PurchaseVerifyResponse, PurchaseGetFirstRewardResponse


def verify(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    provider = request._game_session.provider

    param = request._proto.param

    p = Purchase(server_id, char_id)

    if provider == 'debug':
        raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

    if provider == 'ios':
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
