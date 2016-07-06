# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       task
Date Created:   2015-07-28 11:20
Description:

"""
from utils.http import ProtobufResponse
from core.task import TaskDaily

from protomsg.task_pb2 import TaskDailyGetRewardResponse

def task_daily_get_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    task_id = request._proto.task_id

    resource_classified = TaskDaily(server_id, char_id).get_reward(task_id)

    response = TaskDailyGetRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())
    return ProtobufResponse(response)
