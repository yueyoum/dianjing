# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       session
Date Created:   2016-09-19 14:58
Description:

"""
from django.http import JsonResponse

from core.club import Club
from core.party import Party
from utils.api import APIReturn
from utils.session import GameSession

from config import ConfigErrorMessage

def parse_session(request):
    data = request.body

    try:
        session = GameSession.loads(data)
    except:
        print "API parse_session. Bad Session"
        ret = APIReturn(None)
        ret.code = ConfigErrorMessage.get_error_id("INVALID_OPERATE")
        return JsonResponse(ret.normalize())

    club = Club(session.server_id, session.char_id)

    ret = APIReturn(session.char_id)
    ret.set_data('server_id', club.server_id)
    ret.set_data('char_id', club.char_id)
    ret.set_data('flag', club.flag)
    ret.set_data('name', club.name)

    party_info = Party(session.server_id, session.char_id).get_info()
    ret.set_data('party_info', party_info)

    return JsonResponse(ret.normalize())