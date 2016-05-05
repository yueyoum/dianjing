# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       tower
Date Created:   2016-05-05 17-59
Description:

"""

from utils.http import ProtobufResponse

from core.tower import Tower

from protomsg.tower_pb2 import TowerMatchReportResponse, TowerMatchStartResponse, TowerResetResponse, TowerToMaxStarLevelResponse

def match_start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    level = request._proto.level

    t = Tower(server_id, char_id)
    msg = t.match(level)

    response = TowerMatchStartResponse()
    response.ret = 0
    response.match.MergeFrom(msg)
    return ProtobufResponse(response)

def match_report(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    key = request._proto.level
    star = request._proto.star

    t = Tower(server_id, char_id)

    resource_classified, show_turntable = t.report(key, star)

    response = TowerMatchReportResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())
    response.show_turntable = show_turntable
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
    t.to_max_star_level()

    response = TowerToMaxStarLevelResponse()
    response.ret = 0
    return ProtobufResponse(response)