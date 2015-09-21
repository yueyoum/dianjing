# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       activity
Date Created:   2015-09-21 18:03
Description:

"""

import arrow

from utils.message import MessagePipe
from config import ConfigActivityCategory

from protomsg.activity_pb2 import ActivityCategoryNotify


class ActivityCategory(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def is_show(self, category_id):
        config = ConfigActivityCategory.get(category_id)
        if config.fixed:
            return True

        return config.end_at < arrow.utcnow()

    def send_notify(self):
        notify = ActivityCategoryNotify()

        for cid in ConfigActivityCategory.INSTANCES.keys():
            if not self.is_show(cid):
                continue

            notify_category = notify.categories.add()
            notify_category.id = cid
            if ConfigActivityCategory.get(cid).end_at:
                notify_category.end_at = ConfigActivityCategory.get(cid).end_at.timestamp

        MessagePipe(self.char_id).put(msg=notify)
