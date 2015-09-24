# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       task
Date Created:   2015-07-28 11:20
Description:

"""
from utils.http import ProtobufResponse
from core.task import TaskManager

from protomsg.task_pb2 import TaskAcquireResponse, TaskGetRewardResponse, TaskDoingResponse

def receive(request):
    task_id = request._proto.id
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    task = TaskManager(server_id, char_id)
    task.receive(task_id)

    response = TaskAcquireResponse()
    response.ret = 0
    return ProtobufResponse(response)


def reward(request):
    task_id = request._proto.id
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    task = TaskManager(server_id, char_id)
    drop = task.get_reward(task_id)

    response = TaskGetRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(drop)
    return ProtobufResponse(response)

def doing(request):
    task_id = request._proto.id
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    task = TaskManager(server_id, char_id)
    task.trig_by_id(task_id, 1)

    response = TaskDoingResponse()
    response.ret = 0
    return ProtobufResponse(response)
