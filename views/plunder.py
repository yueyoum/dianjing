# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       plunder
Date Created:   2016-08-22 18:12
Description:

"""

from utils.http import ProtobufResponse

from core.plunder import Plunder
from views.helper import parse_protocol_sync_formation_slots

from protomsg.plunder_pb2 import (
    PlunderFormationSetStaffResponse,
    PlunderFormationSetUnitResponse,
    PlunderReportResponse,
    PlunderSearchResponse,
    PlunderSpyResponse,
    PlunderStartResponse,
    BaseStationSyncResponse,
    PlunderGetRewardResponse,
)

def set_staff(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    way_id = request._proto.way
    slot_id = request._proto.slot_id
    staff_id = request._proto.staff_id

    p = Plunder(server_id, char_id)
    p.set_staff(way_id, slot_id, staff_id)

    response = PlunderFormationSetStaffResponse()
    response.ret = 0
    return ProtobufResponse(response)


def set_unit(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    way_id = request._proto.way
    slot_id = request._proto.slot_id
    unit_id = request._proto.unit_id

    p = Plunder(server_id, char_id)
    p.set_unit(way_id, slot_id, unit_id)

    response = PlunderFormationSetUnitResponse()
    response.ret = 0
    return ProtobufResponse(response)

def search(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    p = Plunder(server_id, char_id)
    p.search()

    response = PlunderSearchResponse()
    response.ret = 0
    return ProtobufResponse(response)

def spy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    target_id = int(request._proto.id)

    p = Plunder(server_id, char_id)
    p.spy(target_id)

    target_plunder = Plunder(server_id, target_id)

    response = PlunderSpyResponse()
    response.ret = 0
    for i in [1, 2 ,3]:
        response_formation = response.formation.add()
        response_formation.MergeFrom(target_plunder.get_way_object(i).make_protobuf())

    return ProtobufResponse(response)

def start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    index = request._proto.index
    formation_slots = parse_protocol_sync_formation_slots(request._proto.slots, policy=1)
    tp = request._proto.tp

    p = Plunder(server_id, char_id)
    match = p.plunder_start(index, tp, formation_slots)

    response = PlunderStartResponse()
    response.ret = 0
    response.match.MergeFrom(match)
    return ProtobufResponse(response)


def report(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    key = request._proto.key
    win = request._proto.win

    p = Plunder(server_id, char_id)
    p.plunder_report(key, win)

    response = PlunderReportResponse()
    response.ret = 0
    return ProtobufResponse(response)


def get_reward(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id


    p = Plunder(server_id, char_id)
    result, drop = p.get_reward()

    response = PlunderGetRewardResponse()
    response.ret = 0
    response.result.extend(result)
    response.drop.MergeFrom(drop.make_protomsg())

    return ProtobufResponse(response)


def sync_station(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    p = Plunder(server_id, char_id)
    p.send_station_notify()

    response = BaseStationSyncResponse()
    response.ret = 0
    return ProtobufResponse(response)


