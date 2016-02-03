# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       system
Date Created:   2016-01-25 18-44
Description:

"""

from apps.system.models import Broadcast
from utils.message import MessagePipe

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.broadcast_pb2 import BroadcastNotify


def send_broadcast_notify(char_id, text=None, repeat_times=1):
    notify = BroadcastNotify()
    if text:
        notify.act = ACT_UPDATE
        b = notify.broadcast.add()
        b.text = text
        b.repeat_times = repeat_times
        MessagePipe(char_id).put(msg=notify)
        return

    broadcasts = Broadcast.objects.filter(display=True)
    if broadcasts.count() == 0:
        return

    notify.act = ACT_INIT
    for cast in broadcasts:
        b = notify.broadcast.add()
        b.text = cast.content
        b.repeat_times = cast.repeat_times

    MessagePipe(char_id).put(msg=notify)

