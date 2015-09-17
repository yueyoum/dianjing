# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       sponsor
Date Created:   2015-09-17 18:30
Description:

"""

from utils.http import ProtobufResponse

from core.sponsor import SponsorManager

from protomsg.spread_pb2 import SponsorGetIncomeResponse, SponsorResponse


def sponsor(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    target_id = request._proto.id

    sm = SponsorManager(server_id, char_id)
    sm.sponsor(target_id)

    response = SponsorResponse()
    response.ret = 0
    return ProtobufResponse(response)


def get_income(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    sm = SponsorManager(server_id, char_id)
    sm.get_income()

    response = SponsorGetIncomeResponse()
    response.ret = 0
    return ProtobufResponse(response)
