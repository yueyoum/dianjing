# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       task
Date Created:   2015-07-28 11:20
Description:

"""
from utils.http import ProtobufResponse
from core.task import RandomEvent

from protomsg.task_pb2 import RandomEventDoneResponse


def random_event_done(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    event_id = request._proto.id

    drop = RandomEvent(server_id, char_id).done(event_id)

    response = RandomEventDoneResponse()
    response.ret = 0
    response.drop.MergeFrom(drop)
    return ProtobufResponse(response)
