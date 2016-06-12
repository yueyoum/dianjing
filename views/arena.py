# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       arena
Date Created:   2016-04-29 16-59
Description:

"""

from utils.http import ProtobufResponse

from core.arena import Arena
from protomsg.arena_pb2 import (
    ArenaHonorGetRewardResponse,
    ArenaLeaderBoardResponse,
    ArenaMatchStartResponse,
    ArenaMatchReportResponse,
    ArenaRefreshResponse,
    ArenaBuyTimesResponse,
)

def buy_times(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    Arena(server_id, char_id).buy_times()

    response = ArenaBuyTimesResponse()
    response.ret = 0
    return ProtobufResponse(response)


def refresh(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    Arena(server_id, char_id).refresh()

    response = ArenaRefreshResponse()
    response.ret = 0
    return ProtobufResponse(response)


def match_start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    rival_id = request._proto.rival_id

    a = Arena(server_id, char_id)
    msg = a.match(rival_id)

    response = ArenaMatchStartResponse()
    response.ret = 0
    response.match.MergeFrom(msg)

    return ProtobufResponse(response)


def match_report(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    key = request._proto.key
    win = request._proto.win

    a = Arena(server_id, char_id)
    resource_classified, rank_changed, max_rank = a.report(key, win)

    response = ArenaMatchReportResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())
    response.rank_changed = rank_changed
    response.max_rank = max_rank
    return ProtobufResponse(response)


def leader_board(request):
    server_id = request._game_session.server_id
    # char_id = request._game_session.char_id

    clubs = Arena.get_leader_board(server_id)

    response = ArenaLeaderBoardResponse()
    response.ret = 0
    for index, club in enumerate(clubs):
        response_rival = response.rival.add()
        response_rival.id = str(club.id)
        response_rival.name = club.name
        response_rival.club_flag = club.flag
        response_rival.level = club.level
        response_rival.power = club.power
        response_rival.rank = index+1

    return ProtobufResponse(response)


def get_honor_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    honor = request._proto.honor

    a = Arena(server_id, char_id)
    resource_classified = a.get_honor_reward(honor)

    response = ArenaHonorGetRewardResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())

    return ProtobufResponse(response)
