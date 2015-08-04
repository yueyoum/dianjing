# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       notification
Date Created:   2015-08-04 18:21
Description:

"""

import arrow

from core.db import MongoDB

from utils.message import MessagePipe

from protomsg.notification_pb2 import NotificationNotify
from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT


class Notification(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = MongoDB.get(server_id)



    def send_notify(self):
        # TODO read data
        data = {
            1: [u"哈哈哈", u"100", u"199", u"29"],
            2: [u"大幅达到是否", u"2323", u"934", u"99"],
            3: [u"看看看", u"99", u"34343"],
            4: [u"i恩爱劳动力", u"834", u"9832"]
        }

        notify = NotificationNotify()
        notify.act = ACT_INIT

        for k, v in data.items():
            notify_noti = notify.notifications.add()
            notify_noti.timestamp = arrow.utcnow().timestamp
            notify_noti.tp = k
            notify_noti.args.extend(v)

        MessagePipe(self.char_id).put(msg=notify)
