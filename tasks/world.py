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

@uwsgidecorators.spool
def broadcast(args):
    from core.mongo import MongoCharacter
    from utils.message import MessagePipe

    try:
        payload = cPickle.loads(args['payload'])
        server_id = payload['server_id']
        exclude_chars = payload['exclude_chars']
        data = payload['data']

        chars = MongoCharacter.db(server_id).find(
            {'_id': {'$nin': exclude_chars}},
            {'_id': 1}
        )

        for c in chars:
            MessagePipe(c['_id']).put(data=data)
    except:
        traceback.print_exc()
