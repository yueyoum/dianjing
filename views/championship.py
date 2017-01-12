# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       championship
Date Created:   2016-12-14 10:31
Description:

"""

from utils.http import ProtobufResponse
from core.championship import Championship

from views.helper import parse_protocol_sync_formation_slots

from protomsg.championship_pb2 import (
    ChampionApplyResponse,
    ChampionBetResponse,
    ChampionFormationSetPositionResponse,
    ChampionFormationSetStaffResponse,
    ChampionFormationSetUnitResponse,
    ChampionGroupSyncResponse,
    ChampionLevelSyncResponse,
)


def set_staff(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    way = request._proto.way
    slot_id = request._proto.slot_id
    staff_id = request._proto.staff_id

    c = Championship(server_id, char_id)
    c.set_staff(way, slot_id, staff_id)

    response = ChampionFormationSetStaffResponse()
    response.ret = 0
    return ProtobufResponse(response)


def set_unit(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    way = request._proto.way
    slot_id = request._proto.slot_id
    unit_id = request._proto.unit_id

    c = Championship(server_id, char_id)
    c.set_unit(way, slot_id, unit_id)

    response = ChampionFormationSetUnitResponse()
    response.ret = 0
    return ProtobufResponse(response)

def set_position(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    way = request._proto.way
    slots = request._proto.slots
    slots = parse_protocol_sync_formation_slots(slots)

    c = Championship(server_id, char_id)
    c.set_position(way, slots)

    response = ChampionFormationSetPositionResponse()
    response.ret = 0
    return ProtobufResponse(response)


def apply_in(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    c = Championship(server_id, char_id)
    c.apply_in()

    response = ChampionApplyResponse()
    response.ret = 0
    return ProtobufResponse(response)

def bet(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    club_id = request._proto.club_id
    bet_id = request._proto.bet_id

    c = Championship(server_id, char_id)
    c.bet(club_id, bet_id)

    response = ChampionBetResponse()
    response.ret = 0
    return ProtobufResponse(response)

def sync_group(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    c = Championship(server_id, char_id)
    c.sync_group()

    response = ChampionGroupSyncResponse()
    response.ret = 0
    return ProtobufResponse(response)

def sync_level(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    c = Championship(server_id, char_id)
    c.sync_level()

    response = ChampionLevelSyncResponse()
    response.ret = 0
    return ProtobufResponse(response)
