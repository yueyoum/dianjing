# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       leaderboard
Date Created:   2016-08-09 15:29
Description:

"""
import arrow

from core.mongo import MongoClubLeaderboard
from core.club import Club
from utils import cache


class ClubLeaderBoard(object):
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    @classmethod
    def generate(cls, server_id):
        char_ids = Club.get_recent_login_char_ids(server_id)

        leaderboard_docs = []

        for cid in char_ids:
            obj = Club(server_id, cid)
            leaderboard_docs.append({
                '_id': cid,
                'level': obj.level,
                'power': obj.power,
            })

        db = MongoClubLeaderboard.db(server_id)
        db.delete_many({})

        if leaderboard_docs:
            db.insert_many(leaderboard_docs)

    def make_cache_key(self):
        return 'club_leaderboard:{0}:{1}'.format(self.server_id, self.char_id)

    def get_info(self):
        info = cache.get(self.make_cache_key())
        if info:
            return info

        # 需要获取新数据
        db = MongoClubLeaderboard.db(self.server_id)

        my_doc = db.find_one({'_id': self.char_id})
        if not my_doc:
            ClubLeaderBoard.generate(self.server_id)
            my_doc = db.find_one({'_id': self.char_id})

        level = []
        power = []
        my_level_rank = 0
        my_power_rank = 0

        rank = 1
        for doc in db.find({}).sort('level', -1).limit(30):
            level.append((doc['_id'], doc['level'], doc['power']))
            if doc['_id'] == self.char_id:
                my_level_rank = rank

            rank += 1

        rank = 1
        for doc in db.find({}).sort('power', -1).limit(30):
            power.append((doc['_id'], doc['level'], doc['power']))
            if doc['_id'] == self.char_id:
                my_power_rank = rank

            rank += 1

        if not my_level_rank:
            my_level_rank = db.find({'level': {'$gte': my_doc['level']}}).count()

        if not my_power_rank:
            my_power_rank = db.find({'power': {'$gte': my_doc['power']}}).count()

        # 下次更新时间
        # NOTE， 注意 定时任务也要同步修改
        now = arrow.utcnow()
        if now.minute >= 30:
            # 下一个小时30分更新
            next_update_at = now.replace(hours=1)
        else:
            next_update_at = now

        # 虽然定时任务是30分启动的，但是这里设定到35分
        next_update_at = next_update_at.replace(minute=35).timestamp

        info = {
            'level': level,
            'power': power,
            'my_level_rank': my_level_rank,
            'my_power_rank': my_power_rank,
            'next_update_at': next_update_at
        }

        expire = next_update_at - now.timestamp
        cache.set(self.make_cache_key(), info, expire=expire)

        return info
