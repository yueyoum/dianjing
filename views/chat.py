# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       chat
Date Created:   2015-08-03 18:21
Description:

"""

from utils.http import ProtobufResponse

from core.chat import Chat

from protomsg.chat_pb2 import ChatSendResponse


def send(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    channel = request._proto.channel
    msg = request._proto.msg
    tp = request._proto.tp

    chat = Chat(server_id, char_id)
    ret = chat.send(tp, channel, msg)

    response = ChatSendResponse()
    response.ret = ret
    return ProtobufResponse(response)
