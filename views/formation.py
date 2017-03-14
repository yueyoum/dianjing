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
    SkillSequenceSetStaffResponse,
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

def skill_sequence_set_staff(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    seq_id = request._proto.seq_id
    index = request._proto.index
    staff_id = request._proto.staff_id

    Formation(server_id, char_id).skill_sequence_set_staff(seq_id, index, staff_id)

    response = SkillSequenceSetStaffResponse()
    response.ret = 0
    return ProtobufResponse(response)
