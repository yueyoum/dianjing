# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       building
Date Created:   2015-07-21 02:29
Description:

"""

from core.building import BuildingManager

from utils.http import ProtobufResponse

from protomsg.building_pb2 import BuildingLevelUpResponse


def levelup(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    building_id = request._proto.id

    bm = BuildingManager(server_id, char_id)
    bm.level_up(building_id)

    response = BuildingLevelUpResponse()
    response.ret = 0
    return ProtobufResponse(response)
