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
    LeagueGetClubDetailInfoResponse,
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

    club_id = request._proto.club_id

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
    response.ret = 0
    response.drop.MergeFrom(drop)

    return ProtobufResponse(response)


def get_detail(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    club_id = request._proto.club_id

    l = LeagueManger(server_id, char_id)
    staffs = l.get_club_detail(club_id)

    response = LeagueGetClubDetailInfoResponse()
    response.ret = 0

    for k, v in staffs.iteritems():
        s = response.detail.add()
        s.staff_id = int(k)
        s.rate_human = 0
        s.rate_bug = 0
        s.rate_god = 0

        if v['winning_rate']:
            for race, value in v['winning_rate'].iteritems():
                if int(race) == 1:
                    s.rate_human = value.get('win', 0) * 100 / value['total']
                elif int(race) == 2:
                    s.rate_bug = value.get('win', 0) * 100 / value['total']
                elif int(race) == 3:
                    s.rate_god = value.get('win', 0) * 100 / value['total']

    return ProtobufResponse(response)

