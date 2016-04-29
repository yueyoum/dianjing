# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       arena
Date Created:   2016-04-29 11-49
Description:

"""

import random

from dianjing.exception import GameException

from core.mongo import MongoArena

from core.club import Club
from core.lock import LockTimeOut, ArenaLock, ArenaMatchLock
from core.cooldown import ArenaRefreshCD, ArenaMatchCD
from core.times_log import TimesLogArenaMatchTimes, TimesLogArenaHonorPoints
from core.match import ClubMatch

from config import ConfigErrorMessage, ConfigArenaNPC, ConfigNPCFormation, ConfigArenaHonorReward

from utils.functional import make_string_id
from utils.message import MessagePipe

from protomsg.arena_pb2 import ArenaNotify, ArenaHonorStatusNotify

ARENA_FREE_TIMES = 10


# NOTE: mongo中的 _id 是 string
# 并且如果是 npc 三个字母开头的 那么就是NPC， 格式是 npc:<npc_id>:<unique_id>
# 从npc_id 就可以从 ConfigNPCFormation 中获取到 阵型

class ArenaClub(object):
    def __new__(cls, server_id, arena_club_id):
        """

        :rtype: core.abstract.AbstractClub
        """
        if arena_club_id.starswith('npc'):
            _, npc_id, _ = arena_club_id.split(':')
            npc_club = ConfigNPCFormation.get(int(npc_id))
            # TODO
            npc_club.name = "NPC-{0}".format(npc_club.id)

            return npc_club

        return Club(server_id, int(arena_club_id))


class Arena(object):
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.try_create_arena_npc()
        self.try_add_self_in_arena()

    def try_create_arena_npc(self):
        if MongoArena.db(self.server_id).count():
            return

        with ArenaLock(self.server_id, self.char_id).lock(hold_seconds=10):
            # 这里要进行double-check
            # 考虑这种情况：
            # 有两个并发的 try_create_arena_npc 调用
            # A先进入，B稍晚进入
            # B 首先判断到 MongoArena 没有记录
            # 然后等待锁， 此时A已经获取了锁，并且最终填充完数据后，B获得锁
            # 此时B必须再进行一次检查，否则B就会生成多余数据
            # double-check 在 多线程的 单例模式 中，也是必备
            if MongoArena.db(self.server_id).count():
                return

            npcs = []
            for i in range(1, 5001):
                # 1 到 5000 个npc
                config = ConfigArenaNPC.get(i)
                npc_id = config.get_npc_id()
                _id = "npc:{0}:{1}".format(npc_id, make_string_id())

                doc = MongoArena.document()
                doc['_id'] = _id
                doc['rank'] = i + 1

                npcs.append(doc)

            MongoArena.db(self.server_id).insert_many(npcs)

    def try_add_self_in_arena(self):
        doc = MongoArena.db(self.server_id).find_one(
            {'_id': str(self.char_id)},
            {'_id': 1}
        )

        if doc:
            return

        with ArenaLock(self.server_id, self.char_id).lock():
            # 这时候要给自己定排名，所以得把整个竞技场锁住，不能让别人插进来
            doc = MongoArena.document()
            doc['_id'] = str(self.char_id)
            doc['rank'] = MongoArena.db(self.server_id).count() + 1
            # 初始化就得刷5个对手出来
            rivals = self.get_rival_list(doc['rank'])
            doc['rivals'] = rivals

            MongoArena.db(self.server_id).insert_one(doc)

    def get_rival_list(self, rank):
        # 获取对手列表
        # TODO rule

        condition = [
            {'rank': {'$gte': rank - 50}},
            {'rank': {'$lte': rank + 50}}
        ]

        docs = MongoArena.db(self.server_id).find({'$and': condition}, {'_id': 1, 'rank': 1})

        results = []
        for doc in docs:
            results.append((doc['_id'], doc['rank']))

        results = random.sample(results, 5)

        results.sort(key=lambda item: item[1])
        return results

    def get_refresh_cd(self):
        return ArenaRefreshCD(self.server_id, self.char_id).get_cd_seconds()

    def get_match_cd(self):
        return ArenaMatchCD(self.server_id, self.char_id).get_cd_seconds()

    def get_remained_match_times(self):
        today_times = TimesLogArenaMatchTimes(self.server_id, self.char_id).count_of_today()
        # TODO vip
        remained = ARENA_FREE_TIMES - today_times
        if remained < 0:
            remained = 0

        return remained

    def get_honor_points(self):
        return TimesLogArenaHonorPoints(self.server_id, self.char_id).count_of_today()

    def refresh(self, ignore_cd=False):
        if not ignore_cd:
            cd = self.get_refresh_cd()
            if cd:
                raise GameException(ConfigErrorMessage.get_error_id("ARENA_REFRESH_IN_CD"))

        doc = MongoArena.db(self.server_id).find_one(
            {'_id': str(self.char_id)},
            {'rank': 1}
        )

        rank = doc['rank']
        rivals = self.get_rival_list(rank)

        MongoArena.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'rivals': rivals
            }}
        )

        if not ignore_cd:
            ArenaRefreshCD(self.server_id, self.char_id).set(5)

        self.send_notify()

    def match(self, rival_id):
        cd = self.get_match_cd()
        if cd:
            raise GameException(ConfigErrorMessage.get_error_id("ARENA_MATCH_IN_CD"))

        doc = MongoArena.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'rivals': 1}
        )

        for _id, _rank in doc['rivals']:
            if _id == rival_id:
                break
        else:
            raise GameException(ConfigErrorMessage.get_error_id("ARENA_RIVAL_NOT_IN_REFRESHED_LIST"))

        rival_doc = MongoArena.db(self.server_id).find_one(
            {'_id': _id},
            {'rank': 1}
        )

        if rival_doc['rank'] != _rank:
            raise GameException(ConfigErrorMessage.get_error_id("ARENA_RIVAL_RANK_CHANGED"))

        try:
            with ArenaMatchLock(self.server_id, self.char_id).lock(hold_seconds=60):
                try:
                    with ArenaMatchLock(self.server_id, rival_id).lock(hold_seconds=60):
                        club_one = Club(self.server_id, self.char_id)
                        club_two = ArenaClub(self.server_id, rival_id)
                        club_match = ClubMatch(club_one, club_two)
                        msg = club_match.start()
                        # TODO set lock key here
                        msg.key = "xxx"
                        return msg
                except LockTimeOut:
                    raise GameException(ConfigErrorMessage.get_error_id("ARENA_RIVAL_IN_MATCH"))
        except LockTimeOut:
            raise GameException(ConfigErrorMessage.get_error_id("ARENA_SELF_IN_MATCH"))

    def report(self, key, win):
        # TODO
        self.refresh(ignore_cd=True)
        self.send_notify()


    @classmethod
    def get_leader_board(cls, server_id, amount=5):
        """

        :rtype: list[core.abstract.AbstractClub]
        """
        docs = MongoArena.db(server_id).find({}, {'_id': 1}).sort('rank').limit(amount)

        clubs = []
        for doc in docs:
            clubs.append(ArenaClub(server_id, doc['_id']))

        return clubs


    def send_honor_notify(self):
        notify = ArenaHonorStatusNotify()
        notify.my_honor = self.get_honor_points()

        for k in ConfigArenaHonorReward.INSTANCES.keys():
            notify_honor = notify.honors.add()
            notify_honor.honor = k
            # TODO
            notify_honor.status = 1

        MessagePipe(self.server_id).put(msg=notify)

    def send_notify(self):
        doc = MongoArena.db(self.server_id).find_one(
            {'_id': str(self.char_id)}
        )

        notify = ArenaNotify()
        notify.my_rank = doc['rank']
        notify.match_cd = self.get_match_cd()
        notify.match_times = self.get_remained_match_times()
        notify.refresh_cd = self.get_refresh_cd()

        for _id, _rank in doc['rivals']:
            notify_rival = notify.rival.add()
            club = ArenaClub(self.server_id, _id)

            notify_rival.id = str(club.id)
            notify_rival.name = club.name
            notify_rival.club_flag = club.flag
            notify_rival.level = club.level
            notify_rival.power = club.power
            notify_rival.rank = _rank

        MessagePipe(self.server_id).put(msg=notify)
