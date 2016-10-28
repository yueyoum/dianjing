# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       inspire
Date Created:   2016-10-28 16:19
Description:

"""

from utils.http import ProtobufResponse
from core.inspire import Inspire

from protomsg.inspire_pb2 import InspireSetStaffResponse

def set_staff(request):
    server_id = request._game_session.server_id
    char_id = request._game_session.char_id

    slot_id = request._proto.slot_id
    staff_id = request._proto.staff_id

    ins = Inspire(server_id, char_id)
    ins.set_staff(slot_id, staff_id)

    response = InspireSetStaffResponse()
    response.ret = 0
    return ProtobufResponse(response)