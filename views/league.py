# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       league
Date Created:   2015-07-23 19:04
Description:

"""

from utils.http import ProtobufResponse
from core.league.league import LeagueManger

from protomsg.league_pb2 import (
    LeagueChallengeResponse,
    LeagueMatchReportResponse,
    LeagueMatchRefreshResponse,
    LeagueGetRewardResponse,
)


def refresh(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    l = LeagueManger(server_id, char_id)
    l.diamond_refresh()

    response = LeagueMatchRefreshResponse()
    response.ret = 0

    return ProtobufResponse(response)


def report(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    key = request._proto.key
    win_club = request._proto.win_club
    result = request._proto.result

    l = LeagueManger(server_id, char_id)
    l.report(key, win_club, result)

    response = LeagueMatchReportResponse()
    response.ret = 0

    return ProtobufResponse(response)


def challenge(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    club_id = request._prot.club_id

    l = LeagueManger(server_id, char_id)
    msg = l.challenge(club_id)

    response = LeagueChallengeResponse()
    response.ret = 0
    response.match.MergeFrom(msg)

    return ProtobufResponse(response)


def get_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    l = LeagueManger(server_id, char_id)
    drop = l.get_daily_reward()

    response = LeagueGetRewardResponse()
    response.drop = drop

    return ProtobufResponse(response)


def get_detail(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    club_id = request._prot.club_id

    l = LeagueManger(server_id, char_id)
    msg = l.get_club_detail(club_id)

    response = LeagueChallengeResponse()
    response.ret = 0
    response.staff.MergeFrom(msg)

    return ProtobufResponse(response)

