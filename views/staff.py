# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       staff
Date Created:   2015-07-10 10:47
Description:

"""

from utils.http import ProtobufResponse
from core.staff import StaffManger

from protomsg.staff_pb2 import (
    StaffRecruitRefreshResponse,
    StaffRecruitResponse,

    StaffDestroyResponse,
    StaffEquipChangeResponse,
    StaffLevelUpResponse,
    StaffStarUpResponse,
    StaffStepUpResponse,
)


def recruit_refresh(request):
    tp = request._proto.tp

    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    recruit = StaffRecruit(server_id, char_id)
    recruit.refresh(tp)

    response = StaffRecruitRefreshResponse()
    response.ret = 0
    return ProtobufResponse(response)


def recruit_staff(request):
    staff_id = request._proto.staff_id

    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    recruit = StaffRecruit(server_id, char_id)
    recruit.recruit(staff_id)

    response = StaffRecruitResponse()
    response.ret = 0
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

    drop = StaffManger(server_id, char_id).destroy(staff_id)

    # FIXME
    response = StaffDestroyResponse()
    response.ret = 0
    for _id, _amount in drop:
        response_drop_item = response.drop.items.add()
        response_drop_item.id = _id
        response_drop_item.amount = _amount
        response_drop_item.tp = 100

    return ProtobufResponse(response)