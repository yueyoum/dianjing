# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2015-07-15 17:43
Description:

"""

from utils.http import ProtobufResponse

from core.challenge import Challenge

from protomsg.challenge_pb2 import (
    ChallengeStartResponse,
    ChallengeBuyEnergyResponse,
    ChallengeMatchReportResponse,
    ChallengeGetStarRewardResponse,
    ChallengeRefreshTimesResponse,
)


def start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    area_id = request._proto.area_id
    challenge_id = request._proto.challenge_id

    c = Challenge(server_id, char_id)
    msg = c.start(int(area_id), int(challenge_id))

    response = ChallengeStartResponse()
    response.ret = 0
    response.match.MergeFrom(msg)

    return ProtobufResponse(response)


def report(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    key = request._proto.key
    win_club = request._proto.win_club
    result = request._proto.result

    drop = Challenge(server_id, char_id).report(key, win_club, result)
    response = ChallengeMatchReportResponse()
    response.ret = 0
    if drop:
        response.drop.MergeFrom(drop)

    return ProtobufResponse(response)


def reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    area_id = request._proto.area_id
    index = request._proto.index

    drop = Challenge(server_id, char_id).get_star_reward(area_id, index)
    response = ChallengeGetStarRewardResponse()
    response.ret = 0
    if drop:
        response.drop.MergeFrom(drop)

    return ProtobufResponse(response)


def buy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    Challenge(server_id, char_id).buy_energy()

    response = ChallengeBuyEnergyResponse()
    response.ret = 0

    return ProtobufResponse(response)


def refresh(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    area_id = request._proto.area_id
    challenge_id = request._proto.challenge_id

    Challenge(server_id, char_id).refresh_challenge_times(area_id, challenge_id)

    response = ChallengeRefreshTimesResponse()
    response.ret = 0

    return ProtobufResponse(response)
