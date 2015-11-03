# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       0001_building_change_to_short_key
Date Created:   2015-11-02 19:02
Description:

以前 buildings 中记录是的 building_id: {current_level: x, complete_time: x}
key太长，会消耗太多内存，所以改成短名字 level, end_at。
并且以前没有训练 complete_time 用的的是-1， 是因为当时设计失误，现在改成0

"""

import os
import sys

sys.path.insert(0, os.getcwd())


def change(sid):
    from core.mongo import MongoBuilding

    for doc in MongoBuilding.db(sid).find():
        _id = doc['_id']

        need_change = False
        for k, v in doc['buildings'].iteritems():
            if 'current_level' in v:
                need_change = True
                break

        if not need_change:
            continue

        buildings = {}
        for k, v in doc['buildings'].iteritems():
            level = v['current_level']
            end_at = v['complete_time']
            if end_at == -1:
                end_at = 0

            buildings[k] = {
                'level': level,
                'end_at': end_at,
            }

        MongoBuilding.db(sid).update_one(
            {'_id': _id},
            {'$set': {'buildings': buildings}}
        )


if __name__ == '__main__':
    import dianjing.wsgi

    from apps.server.models import Server

    for server_id in Server.opened_server_ids():
        change(server_id)
