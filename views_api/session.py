# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       session
Date Created:   2016-09-19 14:58
Description:

"""

from core.club import Club
from core.party import Party
from utils.session import GameSession

from config import ConfigErrorMessage

from api import api_handle
from api.helper import ext_return


@ext_return
def parse_session(request):
    data = request.body
    msg = api_handle.decode(data)
    """:type: api_handle.API.Session.Parse"""

    print msg

    ret = api_handle.API.Session.ParseDone()

    try:
        session = GameSession.loads(msg.session)
    except:
        print "API parse_session. Bad Session"
        ret.ret = ConfigErrorMessage.get_error_id("INVALID_OPERATE")
        return ret

    try:
        club = Club(session.server_id, session.char_id)
    except AssertionError as e:
        print "API error. {0}".format(e.message)
        ret.ret = ConfigErrorMessage.get_error_id("INVALID_OPERATE")
        return ret

    ret.server_id = club.server_id
    ret.char_id = club.char_id
    ret.flag = club.flag
    ret.name = club.name

    party_info = Party(session.server_id, session.char_id).get_info()

    pi = api_handle.API.Session.PartyInfo()

    pi.max_buy_times = party_info['max_buy_times']
    pi.remained_create_times = party_info['remained_create_times']
    pi.remained_join_times = party_info['remained_join_times']
    pi.talent_id = party_info['talent_id']

    ret.partyinfo = pi
    return ret
