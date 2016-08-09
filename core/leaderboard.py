# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       leaderboard
Date Created:   2016-08-09 15:29
Description:

"""
import arrow

from core.mongo import MongoLeaderBoard
from core.club import Club

class BaseLeaderBoard(object):
    __slots__ = ['server_id']
    # 生成间隔秒数
    GENERATE_INTERVAL = 0

    def __init__(self, server_id):
        self.server_id = server_id

    def make_id(self):
        raise NotImplementedError()

    def generate(self):
        raise NotImplementedError()

    def get(self):
        doc = MongoLeaderBoard.db(self.server_id).find_one({'_id': self.make_id()})
        if not doc or arrow.utcnow().timestamp >= doc['generate_at']:
            # 没有，或者过期了
            data, generate_at = self.generate()
        else:
            data = doc['data']
            generate_at = doc['generate_at']

        return data, generate_at + self.GENERATE_INTERVAL


class ClubLeaderBoard(BaseLeaderBoard):
    __slots__ = []
    GENERATE_INTERVAL = 60

    def make_id(self):
        return 'club'

    def generate(self):
        char_ids = Club.get_recent_login_char_ids(self.server_id)

        data = []
        for cid in char_ids:
            obj = Club(self.server_id, cid)
            data.append((cid, obj.level, obj.power))

        # level
        data.sort(key=lambda item: item[1], reverse=True)
        level_data = data[:30]

        # power
        data.sort(key=lambda item: item[2], reverse=True)
        power_data = data[:30]

        data_for_save = {
            'level': level_data,
            'power': power_data
        }

        now = arrow.utcnow().timestamp

        MongoLeaderBoard.db(self.server_id).update_one(
            {'_id': self.make_id()},
            {'$set': {
                'generate_at': now,
                'data': data_for_save
            }},
            upsert=True
        )

        return data_for_save, now
