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
    items = recruit.recruit(tp, mode)

    response = StaffRecruitResponse()
    response.ret = 0
    for _id, _amount in items:
        _item = response.drop.items.add()
        _item.id = _id
        _item.amount = _amount

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
    up_level = request._proto.up_level

    StaffManger(server_id, char_id).level_up(staff_id, up_level)

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

    crit =  StaffManger(server_id, char_id).star_up(staff_id)

    response = StaffStarUpResponse()
    response.ret = 0
    response.crit = crit
    return ProtobufResponse(response)


def destroy(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id
    tp = request._proto.tp

    resource_classified = StaffManger(server_id, char_id).destroy(staff_id, tp)

    response = StaffDestroyResponse()
    response.ret = 0
    response.drop.MergeFrom(resource_classified.make_protomsg())
    return ProtobufResponse(response)