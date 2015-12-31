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

    response = LeagueChallengeResponse()
    response.ret = 0

    for staff in staffs:
        s = response.staff.add()

        s.id = staff['id']
        s.level = staff['level']
        s.cur_exp = staff['cur_exp']
        s.max_exp = staff['max_exp']
        s.status = staff['status']

        s.luoji = staff['luoji']
        s.minjie = staff['minjie']
        s.lilun = staff['lilun']
        s.wuxing = staff['wuxing']
        s.meili = staff['meili']

        s.caozuo = staff['caozuo']
        s.jingying = staff['jingying']
        s.baobing = staff['baobing']
        s.zhanshu = staff['zhanshu']

        s.biaoyan = staff['biaoyan']
        s.yingxiao = staff['yingxiao']
        s.zhimingdu = staff['zhimingdu']

    return ProtobufResponse(response)

