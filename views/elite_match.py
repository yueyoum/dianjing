# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       elite_match
Date Created:   2015-12-10 15:01
Description:

"""

from utils.http import ProtobufResponse

from core.elite_match import EliteMatch

from protomsg.elite_match_pb2 import EliteStartResponse, EliteGetStarRewardResponse, EliteMatchReportResponse


def start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    area_id = request._proto.area_id
    challenge_id = request._proto.challenge_id

    em = EliteMatch(server_id, char_id)
    msg = em.start(area_id, challenge_id)

    response = EliteStartResponse()
    response.ret = 0
    response.match.MergeFrom(msg)

    return ProtobufResponse(response)


def reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    area_id = request._proto.area_id
    index = request._proto.index

    em = EliteMatch(server_id, char_id)
    drop = em.star_reward(area_id, index)

    response = EliteGetStarRewardResponse()
    response.ret = 0
    if drop:
        response.drop.MergeFrom(drop)

    return ProtobufResponse(response)


def report(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    key = request._proto.key
    win_club = request._proto.win_club
    result = request._proto.result

    em = EliteMatch(server_id, char_id)
    drop = em.report(key, win_club, result)

    response = EliteMatchReportResponse()
    response.ret = 0
    if drop:
        response.drop.MergeFrom(response)

    return ProtobufResponse(response)
