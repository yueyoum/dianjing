# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       arena
Date Created:   2016-04-29 16-59
Description:

"""

from utils.http import ProtobufResponse

from core.arena import Arena, ArenaScore
from protomsg.arena_pb2 import (
    ArenaHonorGetRewardResponse,
    ArenaLeaderBoardResponse,
    ArenaMatchStartResponse,
    ArenaMatchReportResponse,
    ArenaRefreshResponse,
    ArenaBuyTimesResponse,
)

from views.helper import parse_protocol_sync_formation_slots

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

    formation_slots = parse_protocol_sync_formation_slots(request._proto.slots)

    a = Arena(server_id, char_id)
    msg = a.match(formation_slots)

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
    resource_classified, score_changed, rank_changed, max_rank, my_rank, my_score = a.report(key, win)

    response = ArenaMatchReportResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())
    response.score_changed = score_changed
    response.rank_changed = rank_changed
    response.max_rank = max_rank
    response.my_rank = my_rank
    response.my_score = my_score
    return ProtobufResponse(response)


def leader_board(request):
    server_id = request._game_session.server_id

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
        response_rival.score = ArenaScore(server_id, club.id).score

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
