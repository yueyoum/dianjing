# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       union
Date Created:   2016-09-30 11:52
Description:

"""

from core.union import Union
from api import api_handle
from api.helper import ext_return, get_extra_msgs

@ext_return
def get_info(request):
    msg = api_handle.decode(request.body)
    """:type: api_handle.API.Union.GetInfo"""

    print msg

    ret = api_handle.API.Union.GetInfoDone()
    ret.ret = 0

    union = Union(msg.server_id, msg.char_id)

    ret.union_id = union.get_joined_union_id()
    ret.owner_id = union.get_joined_union_owner_id()

    ret.extras = get_extra_msgs([msg.char_id])
    return ret
