# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       staff
Date Created:   2015-07-10 10:47
Description:

"""

from utils.http import ProtobufResponse
from core.staff import StaffManger, StaffRecruit

from protomsg.staff_pb2 import (
    StaffRecruitResponse,

    StaffDestroyResponse,
    StaffEquipChangeResponse,
    StaffLevelUpResponse,
    StaffStarUpResponse,
    StaffStepUpResponse,
)


def recruit(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    tp = request._proto.tp
    mode = request._proto.mode

    recruit = StaffRecruit(server_id, char_id)
    resource_classified = recruit.recruit(tp, mode)

    response = StaffRecruitResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())
    return ProtobufResponse(response)


def equipment_change(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id
    slot_id = request._proto.slot_id
    tp = request._proto.tp

    StaffManger(server_id, char_id).equipment_change(staff_id, slot_id, tp)

    response = StaffEquipChangeResponse()
    response.ret = 0
    return ProtobufResponse(response)


def level_up(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id
    item = request._proto.item
    item = [(i.id, i.amount) for i in item]

    StaffManger(server_id, char_id).level_up(staff_id, item)

    response = StaffLevelUpResponse()
    response.ret = 0
    return ProtobufResponse(response)

def step_up(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id

    StaffManger(server_id, char_id).step_up(staff_id)

    response = StaffStepUpResponse()
    response.ret = 0
    return ProtobufResponse(response)

def star_up(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id

    StaffManger(server_id, char_id).star_up(staff_id)

    response = StaffStarUpResponse()
    response.ret = 0
    return ProtobufResponse(response)


def destroy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id

    resource_classified = StaffManger(server_id, char_id).destroy(staff_id)

    response = StaffDestroyResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())
    return ProtobufResponse(response)