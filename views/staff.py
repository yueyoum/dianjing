# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       staff
Date Created:   2015-07-10 10:47
Description:

"""

from utils.http import ProtobufResponse
from core.staff import StaffRecruit, StaffManger

from protomsg.staff_pb2 import (
    StaffRecruitRefreshResponse,
    StaffRecruitResponse,
    StaffFireResponse,
    StaffEquipOnResponse,
    StaffStrengthenResponse,
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


def fire(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id

    sm = StaffManger(server_id, char_id)
    sm.remove(staff_id)

    response = StaffFireResponse()
    response.ret = 0
    return ProtobufResponse(response)

def equip_on(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id
    item_id = request._proto.item_id

    sm = StaffManger(server_id, char_id)
    sm.equipment_on(staff_id, item_id)

    response = StaffEquipOnResponse()
    response.ret = 0
    return ProtobufResponse(response)

def strengthen(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    staff_id = request._proto.staff_id
    item_id = request._proto.item_id

    sm = StaffManger(server_id, char_id)
    sm.strengthen(staff_id, item_id)

    response = StaffStrengthenResponse()
    response.ret = 0
    return ProtobufResponse(response)