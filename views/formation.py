# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       formation
Date Created:   2016-04-12 16-08
Description:

"""

from utils.http import ProtobufResponse

from core.formation import Formation

from protomsg.formation_pb2 import (
    FormationSetStaffResponse,
    FormationSetUnitResponse,
    FormationActiveResponse,
    FormationLevelUpResponse,
    FormationUseResponse,
    FormationSyncResponse,
)

def set_staff(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id
    staff_id = request._proto.staff_id

    f = Formation(server_id, char_id)
    f.set_staff(slot_id, staff_id)

    response = FormationSetStaffResponse()
    response.ret = 0
    return ProtobufResponse(response)


def set_unit(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id
    unit_id = request._proto.unit_id

    f = Formation(server_id, char_id)
    f.set_unit(slot_id, unit_id)

    response = FormationSetUnitResponse()
    response.ret = 0
    return ProtobufResponse(response)


def active(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    fid = request._proto.id

    Formation(server_id, char_id).active_formation(fid)

    response = FormationActiveResponse()
    response.ret = 0
    return ProtobufResponse(response)

def level_up(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    fid = request._proto.id

    Formation(server_id, char_id).levelup_formation(fid)

    response = FormationLevelUpResponse()
    response.ret = 0
    return ProtobufResponse(response)

def use(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    fid = request._proto.id

    Formation(server_id, char_id).use_formation(fid)

    response = FormationUseResponse()
    response.ret = 0
    return ProtobufResponse(response)

def sync(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slots_data = []
    for slot in request._proto.slots:
        slots_data.append((slot.id, slot.index, slot.policy))

    Formation(server_id, char_id).sync_from_client(slots_data)

    response = FormationSyncResponse()
    response.ret = 0
    return ProtobufResponse(response)
