# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       world
Date Created:   2015-09-09 15:45
Description:

"""

import cPickle
import traceback
import uwsgidecorators

from core.club import Club
from utils.message import MessagePipe

@uwsgidecorators.spool
def broadcast(args):
    try:
        payload = cPickle.loads(args['payload'])
        server_id = payload['server_id']
        exclude_chars = payload['exclude_chars']
        data = payload['data']

        # TODO
        # 选择最近在线的用户
        char_ids = Club.get_recent_login_char_ids(server_id)

        for c in char_ids:
            if c not in exclude_chars:
                MessagePipe(c['_id']).put(data=data)
    except:
        traceback.print_exc()
