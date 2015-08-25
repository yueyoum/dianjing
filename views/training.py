# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training
Date Created:   2015-07-21 16:25
Description:

"""

from core.training import TrainingBag, TrainingStore

from utils.http import ProtobufResponse

from protomsg.training_pb2 import TrainingBuyResponse, TrainingStoreRefreshResponse
from protomsg.staff_pb2 import StaffTrainingResponse

def buy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    training_id = request._proto.id

    tr = TrainingBag(server_id, char_id)
    tr.buy(training_id)


    response = TrainingBuyResponse()
    response.ret = 0
    return ProtobufResponse(response)


def refresh(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    TrainingStore(server_id, char_id).refresh()

    response = TrainingStoreRefreshResponse()
    response.ret = 0
    return ProtobufResponse(response)


def training(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id
    training_id = request._proto.training_id

    tr = TrainingBag(server_id, char_id)
    tr.use(staff_id, training_id)

    response = StaffTrainingResponse()
    response.ret = 0
    return ProtobufResponse(response)

