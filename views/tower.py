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
    TowerTurnTableResponse,
    TowerSweepFinishResponse,
    TowerSweepResponse,
    TowerLeaderBoardResponse,
    TowerGoodsBuyResponse,
)

from views.helper import parse_protocol_sync_formation_slots


def match_start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    formation_slots = parse_protocol_sync_formation_slots(request._proto.slots)

    t = Tower(server_id, char_id)
    msg = t.match(formation_slots)

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

    resource_classified, new_star, all_list, sale_goods = t.report(key, star)

    response = TowerMatchReportResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())
    if all_list:
        response.star = new_star
        response.turntable_talent_ids.extend(all_list)

    response.sale_goods = sale_goods
    return ProtobufResponse(response)

def reset(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    t = Tower(server_id, char_id)
    t.reset()

    response = TowerResetResponse()
    response.ret = 0
    return ProtobufResponse(response)

def sweep(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    t = Tower(server_id, char_id)
    t.sweep()

    response = TowerSweepResponse()
    response.ret = 0
    return ProtobufResponse(response)

def sweep_finish(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    t = Tower(server_id, char_id)
    resource_classified = t.sweep_finish()

    response = TowerSweepFinishResponse()
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


def get_leader_board(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    t = Tower(server_id, char_id)
    info = t.get_leader_board()

    response = TowerLeaderBoardResponse()
    response.ret = 0

    for _id, name, star in info:
        response_leaders = response.leaders.add()
        response_leaders.id = str(_id)
        response_leaders.name = name
        response_leaders.star = star

    return ProtobufResponse(response)

def buy_goods(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id
    goods_index = request._proto.goods_index

    t = Tower(server_id, char_id)
    rc = t.buy_goods(goods_index)

    response = TowerGoodsBuyResponse()
    response.ret = 0
    response.drop.MergeFrom(rc.make_protomsg())
    return ProtobufResponse(response)