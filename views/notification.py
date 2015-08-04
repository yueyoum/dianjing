# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       notification
Date Created:   2015-08-04 19:09
Description:

"""

from utils.http import ProtobufResponse

from core.notification import Notification

from protomsg.notification_pb2 import NotificationOpenResponse

def open(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    noti_id = request._proto.id

    n = Notification(server_id, char_id)
    n.open(noti_id)

    response = NotificationOpenResponse()
    response.ret = 0
    return ProtobufResponse(response)
