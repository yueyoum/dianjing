# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       arena
Date Created:   2016-04-29 11-49
Description:

"""

import random

from dianjing.exception import GameException

from core.mongo import MongoArena, MongoArenaScore

from core.club import Club, get_club_property
from core.lock import LockTimeOut, ArenaLock, ArenaMatchLock, remove_lock_key
from core.cooldown import ArenaRefreshCD, ArenaMatchCD
from core.value_log import ValueLogArenaMatchTimes, ValueLogArenaHonorPoints, ValueLogArenaBuyTimes, \
    ValueLogArenaWinTimes
from core.match import ClubMatch
from core.resource import ResourceClassification, money_text_to_item_id
from core.vip import VIP
from core.mail import MailManager
from core.signals import arena_match_signal

from config import ConfigErrorMessage, ConfigArenaNPC, ConfigNPCFormation, ConfigArenaHonorReward, \
    ConfigArenaMatchReward, ConfigArenaBuyTimesCost, ConfigArenaRankReward, ConfigArenaSearchRange

from utils.functional import make_string_id, get_arrow_time_of_today
from utils.message import MessagePipe

from protomsg.arena_pb2 import (
    ArenaNotify,
    ArenaHonorStatusNotify,
    ArenaMatchLogNotify,

    ARENA_HONOR_ALREADY_GOT,
    ARENA_HONOR_CAN_GET,
    ARENA_HONOR_CAN_NOT,
)

ARENA_FREE_TIMES = 5
ARENA_DEFAULT_SCORE = 1000


# NOTE: mongo中的 _id 是 string
# 并且如果是 npc 三个字母开头的 那么就是NPC， 格式是 npc:<npc_id>:<unique_id>
# 从npc_id 就可以从 ConfigNPCFormation 中获取到 阵型

def is_npc_club(arena_club_id):
    return arena_club_id.startswith('npc')


class ArenaClub(object):
    def __new__(cls, server_id, arena_club_id):
        """
        :type server_id: int
        :type arena_club_id: str
        :rtype: core.abstract.AbstractClub
        """
        if is_npc_club(arena_club_id):
            _, npc_id, _ = arena_club_id.split(':')
            npc_club = ConfigNPCFormation.get(int(npc_id))
            # TODO
            npc_club.id = arena_club_id
            npc_club.name = "NPC-{0}".format(npc_id)

            return npc_club

        return Club(server_id, int(arena_club_id))


class MatchTimes(object):
    __slots__ = ['match_times', 'buy_times', 'remained_match_times', 'remained_buy_times', 'buy_cost']

    def __init__(self, server_id, char_id):
        self.match_times = ValueLogArenaMatchTimes(server_id, char_id).count_of_today()
        self.buy_times = ValueLogArenaBuyTimes(server_id, char_id).count_of_today()

        self.remained_match_times = ARENA_FREE_TIMES + self.buy_times - self.match_times
        if self.remained_match_times < 0:
            self.remained_match_times = 0

        self.remained_buy_times = VIP(server_id, char_id).arena_buy_times - self.buy_times
        if self.remained_buy_times < 0:
            self.remained_buy_times = 0

        self.buy_cost = ConfigArenaBuyTimesCost.get_cost(self.buy_times + 1)


class ArenaScore(object):
    __slots__ = ['server_id', 'char_id', 'score']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        doc = MongoArenaScore.db(self.server_id).find_one(
            {'char_ids': str(self.char_id)},
            {'_id': 1}
        )

        if doc:
            self.score = doc['_id']
        else:
            self.score = None

    @property
    def rank(self):
        if not self.score:
            raise RuntimeError("ArenaScore can not calculate rank for None score")

        q1 = MongoArenaScore.db(self.server_id).aggregate([
            {'$match': {'_id': self.score}},
            {'$unwind': {'path': '$char_ids', 'includeArrayIndex': 'index'}},
            {'$match': {'char_ids': str(self.char_id)}}
        ])

        q2 = MongoArenaScore.db(self.server_id).aggregate([
            {'$match': {'_id': {'$gt': self.score}}},
            {'$project': {'amount': {'$size': '$char_ids'}}},
            {'$group': {'_id': None, 'amount': {'$sum': '$amount'}}}
        ])

        q1 = list(q1)
        q2 = list(q2)

        if q2:
            amount = q2[0]['amount']
        else:
            amount = 0

        return amount + q1[0]['index'] + 1

    def set_score(self, score):
        if self.score:
            if self.score == score:
                return

            MongoArenaScore.db(self.server_id).update_one(
                {'_id': self.score},
                {'$pull': {'char_ids': str(self.char_id)}}
            )

        MongoArenaScore.db(self.server_id).update_one(
            {'_id': score},
            {'$push': {'char_ids': str(self.char_id)}},
            upsert=True
        )

        self.score = score

    def add_score(self, score):
        if not self.score:
            raise RuntimeError("ArenaScore can not add score for {0}".format(self.char_id))

        MongoArenaScore.db(self.server_id).update_one(
            {'_id': self.score},
            {'$pull': {'char_ids': str(self.char_id)}}
        )

        self.score += score
        if self.score < ARENA_DEFAULT_SCORE:
            self.score = ARENA_DEFAULT_SCORE

        MongoArenaScore.db(self.server_id).update_one(
            {'_id': self.score},
            {'$push': {'char_ids': str(self.char_id)}},
            upsert=True
        )


class Arena(object):
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.try_add_self_in_arena()

    @classmethod
    def send_rank_reward(cls, server_id):
        char_ids = Club.get_recent_login_char_ids(server_id, recent_days=14)
        char_ids = [str(i) for i in char_ids]

        docs = MongoArena.db(server_id).find({'_id': {'$in': char_ids}}, {'rank': 1})
        for doc in docs:
            cid = doc['_id']
            rank = doc['rank']

            config = ConfigArenaRankReward.get(rank)

            rc = ResourceClassification.classify(config.reward)

            m = MailManager(server_id, int(cid))
            m.add(
                config.mail_title,
                config.mail_content,
                attachment=rc.to_json(),
            )

    @classmethod
    def try_create_arena_npc(cls, server_id):
        if MongoArena.db(server_id).count():
            return

        with ArenaLock(server_id, None).lock(hold_seconds=20):
            # 这里要进行double-check
            # 考虑这种情况：
            # 有两个并发的 try_create_arena_npc 调用
            # A先进入，B稍晚进入
            # B 首先判断到 MongoArena 没有记录
            # 然后等待锁， 此时A已经获取了锁，并且最终填充完数据后，B获得锁
            # 此时B必须再进行一次检查，否则B就会生成多余数据
            # double-check 在 多线程的 单例模式 中，也是必备
            if MongoArena.db(server_id).count():
                return

            npcs = []

            for _, v in ConfigArenaNPC.INSTANCES.iteritems():
                for _ in range(v.amount):
                    npc_id = random.choice(v.npcs)
                    _id = "npc:{0}:{1}".format(npc_id, make_string_id())

                    doc = MongoArena.document()
                    doc['_id'] = _id
                    npcs.append(doc)

                    score = random.randint(v.score_low, v.score_high)
                    ArenaScore(server_id, _id).set_score(score)

            MongoArena.db(server_id).insert_many(npcs)

    def try_add_self_in_arena(self):
        doc = MongoArena.db(self.server_id).find_one(
            {'_id': str(self.char_id)},
            {'honor_rewards': 1}
        )

        if doc:
            # 清理过期的 honor_rewards 记录
            honor_rewards = doc.get('honor_rewards', {})
            if not honor_rewards:
                return

            today_key = str(get_arrow_time_of_today().timestamp)

            unset = {}
            for k in honor_rewards.keys():
                if k != today_key:
                    unset['honor_rewards.{0}'.format(k)] = 1

            if unset:
                MongoArena.db(self.server_id).update_one(
                    {'_id': str(self.char_id)},
                    {'$unset': unset}
                )

            return

        doc = MongoArena.document()
        doc['_id'] = str(self.char_id)
        MongoArena.db(self.server_id).insert_one(doc)

        ArenaScore(self.server_id, self.char_id).set_score(ARENA_DEFAULT_SCORE)

    def get_current_rank(self):
        return ArenaScore(self.server_id, self.char_id).rank

    def get_max_rank(self):
        doc = MongoArena.db(self.server_id).find_one(
            {'_id': str(self.char_id)},
            {'max_rank': 1}
        )

        max_rank = doc['max_rank']
        if max_rank:
            return max_rank

        return self.get_current_rank()

    def check_max_rank(self, rank):
        max_rank = self.get_max_rank()
        if rank > max_rank:
            raise GameException(ConfigErrorMessage.get_error_id("ARENA_MAX_RANK_CHECK_FAILURE"))

    def search_rival(self, search_times=0):
        # 获取对手列表
        def _query(low, high):
            condition = [
                {'_id': {'$gte': low}},
                {'_id': {'$lte': high}},
            ]

            docs = MongoArenaScore.db(self.server_id).find({'$and': condition})
            for doc in docs:
                if doc['char_ids']:
                    cid = random.choice(doc['char_ids'])
                    if cid != str(self.char_id):
                        return cid

            return None

        if not search_times:
            doc = MongoArena.db(self.server_id).find_one(
                {'_id': str(self.char_id)},
                {'search_times': 1}
            )

            search_times = doc['search_times']

        my_score = ArenaScore(self.server_id, self.char_id).score
        #
        # while True:
        #     search_config = ConfigArenaSearchRange.get(search_times)

        # TODO real rule
        result = _query(my_score * 0.1, my_score * 10)
        if not result:
            result = _query(ARENA_DEFAULT_SCORE, 100000)
            assert result

        return result

    def get_refresh_cd(self):
        return ArenaRefreshCD(self.server_id, self.char_id).get_cd_seconds()

    def get_match_cd(self):
        return ArenaMatchCD(self.server_id, self.char_id).get_cd_seconds()

    def get_honor_points(self):
        return ValueLogArenaHonorPoints(self.server_id, self.char_id).count_of_today()

    def buy_times(self):
        rt = MatchTimes(self.server_id, self.char_id)
        if not rt.remained_buy_times:
            raise GameException(ConfigErrorMessage.get_error_id("ARENA_NO_BUY_TIMES"))

        cost = [(money_text_to_item_id('diamond'), rt.buy_cost), ]
        rc = ResourceClassification.classify(cost)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id)

        ValueLogArenaBuyTimes(self.server_id, self.char_id).record()

        self.send_notify()

    def add_point(self, point):
        assert point > 0
        MongoArena.db(self.server_id).update_one(
            {'_id': str(self.char_id)},
            {'$inc': {
                'point': point
            }}
        )
        self.send_notify()

    def check_point(self, point):
        doc = MongoArena.db(self.server_id).find_one(
            {'_id': str(self.char_id)},
            {'point': 1}
        )

        current_point = doc.get('point', 0)
        new_point = current_point - point
        if new_point < 0:
            raise GameException(ConfigErrorMessage.get_error_id("ARENA_POINT_NOT_ENOUGH"))

        return new_point

    def remove_point(self, point):
        new_point = self.check_point(point)
        MongoArena.db(self.server_id).update_one(
            {'_id': str(self.char_id)},
            {'$set': {'point': new_point}}
        )
        self.send_notify()

    def refresh(self, ignore_cd=False):
        if not ignore_cd:
            cd = self.get_refresh_cd()
            if cd:
                raise GameException(ConfigErrorMessage.get_error_id("ARENA_REFRESH_IN_CD"))

        rival = self.search_rival()

        MongoArena.db(self.server_id).update_one(
            {'_id': str(self.char_id)},
            {'$set': {
                'rival': rival
            }}
        )

        if not ignore_cd:
            ArenaRefreshCD(self.server_id, self.char_id).set(5)

        self.send_notify()

    def check_and_buy_times(self):
        rt = MatchTimes(self.server_id, self.char_id)
        cost = [(money_text_to_item_id('diamond'), rt.buy_cost), ]
        rc = ResourceClassification.classify(cost)

        if not rt.remained_match_times:
            if not rt.remained_buy_times:
                raise GameException(ConfigErrorMessage.get_error_id("ARENA_NO_BUY_TIMES"))

            rc.check_exist(self.server_id, self.char_id)
            rc.remove(self.server_id, self.char_id)
            ValueLogArenaBuyTimes(self.server_id, self.char_id).record()

            self.send_notify()

    def match(self):
        if self.get_match_cd():
            raise GameException(ConfigErrorMessage.get_error_id("ARENA_MATCH_IN_CD"))

        doc = MongoArena.db(self.server_id).find_one(
            {'_id': str(self.char_id)},
            {'rival': 1}
        )

        rival_id = doc['rival']

        if not rival_id:
            # TODO error code
            raise GameException(ConfigErrorMessage.get_error_id("ARENA_RIVAL_NOT_IN_REFRESHED_LIST"))

        self.check_and_buy_times()

        try:
            with ArenaMatchLock(self.server_id, self.char_id).lock(hold_seconds=180) as my_lock:
                try:
                    with ArenaMatchLock(self.server_id, rival_id).lock(hold_seconds=180) as rival_lock:
                        club_one = Club(self.server_id, self.char_id)
                        club_two = ArenaClub(self.server_id, rival_id)
                        club_match = ClubMatch(club_one, club_two)
                        msg = club_match.start()
                        # NOTE: rival_id 如果是NPC的话， 本来里面就是:分割的。 这里不能再用:
                        msg.key = "{0}#{1}#{2}".format(rival_id, my_lock.key, rival_lock.key)
                        return msg
                except LockTimeOut:
                    raise GameException(ConfigErrorMessage.get_error_id("ARENA_RIVAL_IN_MATCH"))
        except LockTimeOut:
            raise GameException(ConfigErrorMessage.get_error_id("ARENA_SELF_IN_MATCH"))

    def report(self, key, win):
        # 这里self 和 rival 都应该处于 lock 状态
        rival_id, my_lock_key, rival_lock_key = key.split('#')

        my_club_name = get_club_property(self.server_id, self.char_id, 'name')

        my_rank = self.get_current_rank()
        my_max_rank = self.get_max_rank()

        # TODO real add score
        ass = ArenaScore(self.server_id, self.char_id)
        ass.add_score(100 if win else -100)

        new_rank = ass.rank
        if new_rank > my_max_rank:
            my_max_rank = new_rank

            MongoArena.db(self.server_id).update_one(
                {'_id': str(self.char_id)},
                {'$set': {'max_rank': new_rank}}
            )

        rank_changed = new_rank - my_rank

        rival_rank = Arena(self.server_id, rival_id).get_current_rank()

        if win:
            ValueLogArenaWinTimes(self.server_id, self.char_id).record()

            if my_rank > rival_rank:
                if not is_npc_club(rival_id):
                    Arena(self.server_id, int(rival_id)).add_match_log(3, [my_club_name, str(rank_changed)])
            else:
                if not is_npc_club(rival_id):
                    Arena(self.server_id, int(rival_id)).add_match_log(2, [my_club_name])

            config = ConfigArenaMatchReward.get(1)
        else:
            config = ConfigArenaMatchReward.get(2)
            if not is_npc_club(rival_id):
                Arena(self.server_id, int(rival_id)).add_match_log(1, [my_club_name])

        ValueLogArenaHonorPoints(self.server_id, self.char_id).record(value=config.honor)
        ValueLogArenaMatchTimes(self.server_id, self.char_id).record()

        drop = config.get_drop()
        resource_classified = ResourceClassification.classify(drop)
        resource_classified.add(self.server_id, self.char_id)

        self.refresh(ignore_cd=True)
        # TODO cd
        ArenaMatchCD(self.server_id, self.char_id).set(0)

        self.send_honor_notify()
        self.send_notify()

        remove_lock_key(my_lock_key)
        remove_lock_key(rival_lock_key)

        arena_match_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            target_id=rival_id,
            target_name=ArenaClub(self.server_id, rival_id).name,
            my_rank=new_rank,
            target_rank=rival_rank,
            win=win,
        )

        return resource_classified, rank_changed, my_max_rank, new_rank

    def get_today_honor_reward_info(self):
        today_key = str(get_arrow_time_of_today().timestamp)
        doc = MongoArena.db(self.server_id).find_one(
            {'_id': str(self.char_id)},
            {'honor_rewards.{0}'.format(today_key): 1}
        )

        return doc.get('honor_rewards', {}).get(today_key, [])

    def get_honor_reward(self, honor_id):
        config = ConfigArenaHonorReward.get(honor_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if honor_id > self.get_honor_points():
            raise GameException(ConfigErrorMessage.get_error_id("ARENA_HONOR_REWARD_POINT_NOT_ENOUGH"))

        reward_info = self.get_today_honor_reward_info()
        if honor_id in reward_info:
            raise GameException(ConfigErrorMessage.get_error_id("ARENA_HONOR_REWARD_ALREADY_GOT"))

        resource_classified = ResourceClassification.classify(config.reward)
        resource_classified.add(self.server_id, self.char_id)

        today_key = str(get_arrow_time_of_today().timestamp)
        MongoArena.db(self.server_id).update_one(
            {'_id': str(self.char_id)},
            {
                '$push': {
                    'honor_rewards.{0}'.format(today_key): honor_id
                }
            }
        )

        reward_info.append(honor_id)
        self.send_honor_notify(reward_info=reward_info)
        return resource_classified

    def add_match_log(self, _id, _argument):
        log = [_id, _argument]

        MongoArena.db(self.server_id).update_one(
            {'_id': str(self.char_id)},
            {
                '$push': {
                    'logs': {
                        '$each': [log],
                        '$slice': -50,
                    }
                }
            }
        )

        self.send_match_log_notify()

    @classmethod
    def get_leader_board(cls, server_id, amount=30):
        """

        :rtype: list[core.abstract.AbstractClub]
        """
        docs = MongoArena.db(server_id).find({}, {'_id': 1}).sort('rank').limit(amount)

        clubs = []
        for doc in docs:
            clubs.append(ArenaClub(server_id, doc['_id']))

        return clubs

    def send_honor_notify(self, reward_info=None):
        if not reward_info:
            reward_info = self.get_today_honor_reward_info()

        my_honor = self.get_honor_points()

        notify = ArenaHonorStatusNotify()
        notify.my_honor = my_honor

        for k in ConfigArenaHonorReward.INSTANCES.keys():
            notify_honor = notify.honors.add()
            notify_honor.honor = k

            if k in reward_info:
                notify_honor.status = ARENA_HONOR_ALREADY_GOT
            elif k <= my_honor:
                notify_honor.status = ARENA_HONOR_CAN_GET
            else:
                notify_honor.status = ARENA_HONOR_CAN_NOT

        MessagePipe(self.char_id).put(msg=notify)

    def send_match_log_notify(self):
        doc = MongoArena.db(self.server_id).find_one(
            {'_id': str(self.char_id)},
            {'logs': []}
        )

        logs = doc.get('logs', [])
        notify = ArenaMatchLogNotify()
        for _id, _arguments in logs:
            notify_log = notify.logs.add()
            notify_log.id = _id
            notify_log.arguments.extend(_arguments)

        MessagePipe(self.char_id).put(msg=notify)

    def send_notify(self):
        doc = MongoArena.db(self.server_id).find_one(
            {'_id': str(self.char_id)}
        )

        rt = MatchTimes(self.server_id, self.char_id)

        notify = ArenaNotify()
        notify.my_rank = self.get_current_rank()
        notify.match_cd = self.get_match_cd()
        notify.refresh_cd = self.get_refresh_cd()

        notify.match_times = rt.remained_match_times
        notify.buy_times = rt.remained_buy_times
        notify.buy_cost = rt.buy_cost
        notify.point = doc.get('point', 0)
        notify.max_rank = self.get_max_rank()

        if doc['rival']:
            notify_rival = notify.rival.add()
            club = ArenaClub(self.server_id, doc['rival'])

            notify_rival.id = str(club.id)
            notify_rival.name = club.name
            notify_rival.club_flag = club.flag
            notify_rival.level = club.level
            notify_rival.power = club.power
            notify_rival.rank = Arena(self.server_id, doc['rival']).get_current_rank()

        MessagePipe(self.char_id).put(msg=notify)
