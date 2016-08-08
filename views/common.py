# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       sync
Date Created:   2015-08-03 18:26
Description:

"""
from core.signals import game_start_signal
from utils.http import ProtobufResponse

from protomsg.common_pb2 import SyncResponse, PingResponse

# 全部同步，相当于登陆
def sync(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    param = request._proto.param

    game_start_signal.send(
        sender=None,
        server_id=server_id,
        char_id=char_id,
    )

    response = SyncResponse()
    response.ret = 0
    response.param = param
    return ProtobufResponse(response)

def ping(request):
    response = PingResponse()
    response.ret = 0
    return ProtobufResponse(response)
