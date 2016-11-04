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

from core.union import Union

from utils.operation_log import OperationLog
from utils.message import MessagePipe


@uwsgidecorators.spool
def broadcast(args):
    try:
        payload = cPickle.loads(args['payload'])
        server_id = payload['server_id']
        exclude_chars = payload['exclude_chars']
        data = payload['data']
    except:
        traceback.print_exc()
        return

    char_ids = OperationLog.get_recent_action_char_ids(server_id)
    for cid in char_ids:
        if cid not in exclude_chars:
            MessagePipe(cid).put(data=data)


@uwsgidecorators.spool
def broadcast_union_chat(args):
    try:
        payload = cPickle.loads(args['payload'])
        server_id = payload['server_id']
        exclude_chars = payload['exclude_chars']
        data = payload['data']
        char_id = payload['char_id']
    except:
        traceback.print_exc()
        return

    union = Union(server_id, char_id)
    member_ids = union.get_member_ids()

    for cid in member_ids:
        if cid not in exclude_chars:
            MessagePipe(cid).put(data=data)
