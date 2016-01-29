# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training_match
Date Created:   2015-12-08 18:36
Description:

"""

from utils.http import ProtobufResponse

from core.training_match import TrainingMatch

from protomsg.training_match_pb2 import (
    TrainingMatchReportResponse,
    TrainingMatchStartResponse,
    TrainingMatchGetMatchClubDetailResponse,
)


def start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    index = request._proto.club_index

    tm = TrainingMatch(server_id, char_id)
    msg = tm.start(index)

    response = TrainingMatchStartResponse()
    response.ret = 0
    response.match.MergeFrom(msg)

    return ProtobufResponse(response)


def match_report(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    is_win = request._proto.is_win
    key = request._proto.key
    result = request._proto.result

    tm = TrainingMatch(server_id, char_id)
    drop = tm.match_report(is_win, key)

    response = TrainingMatchReportResponse()
    response.ret = 0
    if drop:
        response.drop.MergeFrom(drop)

    return ProtobufResponse(response)


def match_detail(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    index = request._proto.club_index
    tm = TrainingMatch(server_id, char_id)

    staffs = tm.get_match_detail(index)
    response = TrainingMatchGetMatchClubDetailResponse()
    response.ret = 0

    for k, v in staffs.iteritems():
        staff_detail = response.staffs.add()
        staff_detail.staff_id = k
        staff_detail.staff_level = v.level

    return ProtobufResponse(response)
