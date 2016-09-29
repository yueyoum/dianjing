# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       helper
Date Created:   2016-09-29 16:39
Description:

"""

from django.http import HttpResponse
from utils.message import MessagePipe

from api import api_handle


def ext_return(func):
    def deco(*args, **kwargs):
        msg = func(*args, **kwargs)
        return HttpResponse(api_handle.encode(msg), content_type='text/plain')

    return deco


def get_extra_msgs(char_ids):
    extras = []
    for cid in char_ids:
        msgs = MessagePipe(cid).get()
        # 去掉头部4字节长度， erlang发送的时候会自己添加
        msgs = [msg[4:] for msg in msgs]

        ex = api_handle.API.Common.ExtraReturn()
        ex.char_id = cid
        ex.msgs = msgs

        extras.append(ex)

    return extras
