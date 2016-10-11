# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       system
Date Created:   2016-01-25 18-44
Description:

"""

import cPickle

from core.club import get_club_property

from utils.message import MessagePipe, MessageFactory

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.broadcast_pb2 import BroadcastNotify

from config import ConfigBroadcastTemplate, ConfigItemNew


def send_system_notify(char_id):
    from apps.config.models import Broadcast as ModelBroadcast

    broadcasts = ModelBroadcast.objects.filter(display=True)
    if broadcasts.count() == 0:
        return

    notify = BroadcastNotify()
    notify.act = ACT_INIT
    for cast in broadcasts:
        b = notify.broadcast.add()
        b.text = cast.content
        b.repeat_times = cast.repeat_times

    MessagePipe(char_id).put(msg=notify)


class BroadCast(object):
    __slots__ = ['server_id', 'char_id', 'name']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.name = get_club_property(server_id, char_id, 'name')

    def try_cast_login_notify(self):
        # 这个玩家登陆要广播的消息
        from core.arena import Arena
        top = Arena.get_leader_board(self.server_id, amount=1)
        if top and top[0].id == self.char_id:
            template = ConfigBroadcastTemplate.get(4).template
            text = template.format(self.name)
            self.do_cast(text)

    def cast_staff_step_up_notify(self, staff_original_id, step_level):
        template = ConfigBroadcastTemplate.get(1).template
        text = template.format(self.name, ConfigItemNew.get(staff_original_id).name, step_level)
        self.do_cast(text)

    def cast_staff_star_up_notify(self, staff_original_id, star):
        template = ConfigBroadcastTemplate.get(2).template
        text = template.format(self.name, ConfigItemNew.get(staff_original_id).name, star)
        self.do_cast(text)

    def cast_arena_match_notify(self, continue_win):
        template = ConfigBroadcastTemplate.get(3).template
        text = template.format(self.name, continue_win)
        self.do_cast(text)

    def cast_diamond_recruit_staff_notify(self, staff_original_id):
        template = ConfigBroadcastTemplate.get(5).template
        text = template.format(self.name, ConfigItemNew.get(staff_original_id).name)
        self.do_cast(text)

    def do_cast(self, text, repeat_times=1):
        from tasks import world

        notify = BroadcastNotify()
        notify.act = ACT_UPDATE
        b = notify.broadcast.add()
        b.text = text
        b.repeat_times = repeat_times

        data = MessageFactory.pack(notify)

        # 先发给自己，确保自己能立即看到
        MessagePipe(self.char_id).put(data=data)

        # 再发给其他人
        arg = {
            'server_id': self.server_id,
            'exclude_chars': [self.char_id],
            'data': data
        }

        payload = cPickle.dumps(arg)
        world.broadcast(payload=payload)
