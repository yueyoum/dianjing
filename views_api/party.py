# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       party
Date Created:   2016-09-19 16:01
Description:

"""

from core.party import Party
from api import api_handle
from api.helper import ext_return, get_extra_msgs


@ext_return
def create(request):
    msg = api_handle.decode(request.body)
    """:type: api_handle.API.Party.Create"""

    print msg

    p = Party(msg.server_id, msg.char_id)
    ret = p.create(msg.party_level)
    ret.extras = get_extra_msgs([msg.char_id])
    return ret


@ext_return
def join(request):
    msg = api_handle.decode(request.body)
    """:type: api_handle.API.Party.Join"""

    print msg

    p = Party(msg.server_id, msg.char_id)
    ret = p.join(msg.owner_id)
    ret.extras = get_extra_msgs([msg.char_id])
    return ret


@ext_return
def start(request):
    msg = api_handle.decode(request.body)
    """:type: api_handle.API.Party.Start"""

    print msg

    p = Party(msg.server_id, msg.char_id)
    ret = p.start(msg.party_level, msg.members)
    ret.extras = get_extra_msgs([msg.char_id])

    return ret


@ext_return
def buy(request):
    msg = api_handle.decode(request.body)
    """:type: api_handle.API.Party.Buy"""

    print msg

    p = Party(msg.server_id, msg.char_id)
    ret = p.buy_item(msg.party_level, msg.buy_id, msg.members)

    # all_char_ids = [msg.char_id]
    # all_char_ids.extend(msg.members)
    ret.extras = get_extra_msgs([msg.char_id])
    return ret


@ext_return
def end(request):
    msg = api_handle.decode(request.body)
    """:type: api_handle.API.Party.End"""

    print msg

    p = Party(msg.server_id, msg.char_id)
    ret = p.end(msg.party_level, msg.members)

    # all_char_ids = [msg.char_id]
    # all_char_ids.extend(msg.members)
    # ret.extras = get_extra_msgs([msg.char_id])
    ret.extras = []
    return ret
