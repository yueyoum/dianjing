# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       sync
Date Created:   2015-08-03 18:26
Description:

"""

from utils.http import ProtobufResponse

from protomsg.common_pb2 import SyncResponse, PingResponse

def sync(request):
    # server_id = request._game_session.server_id
    # char_id = request._game_session.char_id

    response = SyncResponse()
    response.ret = 0
    return ProtobufResponse(response)

def ping(request):
    response = PingResponse()
    response.ret = 0
    return ProtobufResponse(response)
