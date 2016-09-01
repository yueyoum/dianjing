# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       plunder
Date Created:   2016-08-22 18:12
Description:

"""

from utils.http import ProtobufResponse

from core.plunder import Plunder, SpecialEquipmentGenerator
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
    PlunderBuyTimesResponse,

    SpecialEquipmentGenerateResponse,
    SpecialEquipmentGenerateSpeedUpResponse,
    SpecialEquipmentGetResponse,
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

    response = PlunderSpyResponse()
    response.ret = 0
    return ProtobufResponse(response)

def start(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    _id = request._proto.id
    formation_slots = parse_protocol_sync_formation_slots(request._proto.slots, policy=1)
    tp = request._proto.tp

    if request._proto.HasField('win'):
        win = request._proto.win
    else:
        win = None

    p = Plunder(server_id, char_id)
    match = p.plunder_start(_id, tp, formation_slots, win)

    response = PlunderStartResponse()
    response.ret = 0
    if match:
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


def buy_plunder_times(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    p = Plunder(server_id, char_id)
    p.buy_plunder_times()

    response = PlunderBuyTimesResponse()
    response.ret = 0
    return ProtobufResponse(response)


def sync_station(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    p = Plunder(server_id, char_id)
    p.send_station_notify()
    p.send_plunder_times_notify()

    response = BaseStationSyncResponse()
    response.ret = 0
    return ProtobufResponse(response)


def special_equipment_generate(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id
    tp = request._proto.tp

    s = SpecialEquipmentGenerator(server_id, char_id)
    s.generate(slot_id, tp)

    response = SpecialEquipmentGenerateResponse()
    response.ret = 0
    return ProtobufResponse(response)

def special_equipment_speedup(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    s = SpecialEquipmentGenerator(server_id, char_id)
    s.speedup()

    response = SpecialEquipmentGenerateSpeedUpResponse()
    response.ret = 0
    return ProtobufResponse(response)

def special_equipment_get(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    s = SpecialEquipmentGenerator(server_id, char_id)
    equip = s.get_result()

    response = SpecialEquipmentGetResponse()
    response.ret = 0
    response.equipment.MergeFrom(equip.make_protomsg())
    return ProtobufResponse(response)
