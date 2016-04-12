# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       formation
Date Created:   2016-04-12 16-08
Description:

"""

from utils.http import ProtobufResponse

from core.formation import Formation

from protomsg.formation_pb2 import FormationMoveSlotResponse, FormationSetStaffResponse, FormationSetUnitResponse

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

def move_slot(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id
    to_index = request._proto.to_index

    f = Formation(server_id, char_id)
    f.move_slot(slot_id, to_index)

    response = FormationMoveSlotResponse()
    response.ret = 0
    return ProtobufResponse(response)