# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       tower
Date Created:   2016-05-05 17-59
Description:

"""

from utils.http import ProtobufResponse

from core.tower import Tower

from protomsg.tower_pb2 import (
    TowerMatchReportResponse,
    TowerMatchStartResponse,
    TowerResetResponse,
    TowerToMaxStarLevelResponse,
    TowerTurnTableResponse,
)


def match_start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    t = Tower(server_id, char_id)
    msg = t.match()

    response = TowerMatchStartResponse()
    response.ret = 0
    response.match.MergeFrom(msg)
    return ProtobufResponse(response)

def match_report(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    key = request._proto.key
    star = request._proto.star

    t = Tower(server_id, char_id)

    resource_classified, new_star, all_list = t.report(key, star)

    response = TowerMatchReportResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())
    if all_list:
        response.star = new_star
        response.turntable_talent_ids.extend(all_list)
    return ProtobufResponse(response)

def reset(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    t = Tower(server_id, char_id)
    t.reset()

    response = TowerResetResponse()
    response.ret = 0
    return ProtobufResponse(response)

def to_max_star_level(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    t = Tower(server_id, char_id)
    resource_classified =  t.to_max_star_level()

    response = TowerToMaxStarLevelResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())
    return ProtobufResponse(response)

def turntable_pick(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    star = request._proto.star

    t = Tower(server_id, char_id)
    index = t.turntable_pick(star)

    response = TowerTurnTableResponse()
    response.ret = 0
    response.got_index = index
    return ProtobufResponse(response)
