# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       ladder
Date Created:   2015-08-13 16:26
Description:

"""

import random
import arrow

import pymongo

from dianjing.exception import GameException

from core.mongo import MongoLadder
from core.abstract import AbstractStaff, AbstractClub
from core.club import Club
from core.match import ClubMatch
from core.common import CommonLadderStore
from core.package import Drop
from core.resource import Resource
from core.notification import Notification
from core.mail import MailManager

from core.lock import Lock, LadderLock, LadderNPCLock, LadderStoreLock, LockTimeOut

from utils.functional import make_string_id
from utils.message import MessagePipe

from config import (
    ConfigLadderScoreStore,
    ConfigLadderRankReward,
    ConfigNPC,
    ConfigErrorMessage,
    ConfigStaff,
)
from config.settings import LADDER_LOG_MAX_AMOUNT

from protomsg.ladder_pb2 import LadderNotify, LadderStoreNotify

NPC_AMOUNT = 2000
DEFAULT_MATCH_TIMES = 10


class LadderNPCStaff(AbstractStaff):
    def __init__(self, data):
        super(LadderNPCStaff, self).__init__()

        self.id = data['id']
        config = ConfigStaff.get(self.id)

        # TODO
        self.level = 1
        self.race = config.race

        self.jingong = data['jingong']
        self.qianzhi = data['qianzhi']
        self.xintai = data['xintai']
        self.baobing = data['baobing']
        self.fangshou = data['fangshou']
        self.yunying = data['yunying']
        self.yishi = data['yishi']
        self.caozuo = data['caozuo']

        skill_level = data.get('skill_level', 1)
        self.skills = {i: skill_level for i in config.skill_ids}


class LadderNPCClub(AbstractClub):
    def __init__(self, ladder_id, club_name, manager_name, club_flag, staffs, order, score):
        super(LadderNPCClub, self).__init__()
        self.id = ladder_id
        self.name = club_name
        self.manager_name = manager_name
        self.flag = club_flag
        # TODO
        self.policy = 1

        for s in staffs:
            self.match_staffs.append(s['id'])
            self.staffs[s['id']] = LadderNPCStaff(s)

        self.order = order
        self.score = score


class LadderRealClub(Club):
    def __init__(self, server_id, club_id, order, score):
        super(LadderRealClub, self).__init__(server_id, club_id)
        self.order = order
        self.score = score


class LadderClub(object):
    def __new__(cls, server_id, club):
        # club 是 Ladder 数据
        if club['club_name']:
            # NPC
            return LadderNPCClub(club['_id'], club['club_name'], club['manager_name'], club['club_flag'],
                                 club['staffs'], club['order'], club['score'])

        return LadderRealClub(server_id, int(club['_id']), club['order'], club['score'])


class LadderMatch(object):
    def __init__(self, server_id, club_one, club_two):
        self.server_id = server_id
        self.club_one = club_one
        self.club_two = club_two

        self.club_one_object = LadderClub(self.server_id, self.club_one)
        self.club_two_object = LadderClub(self.server_id, self.club_two)

        self.club_one_win = False

    def start(self):
        match = ClubMatch(self.club_one_object, self.club_two_object)
        msg = match.start()
        self.club_one_win = msg.club_one_win

        self.after_match()
        return msg

    def after_match(self):
        # 记录天梯战报
        order_changed = self.club_one['order'] - self.club_two['order']

        # final_club_one_order = self.club_one['order']
        final_club_two_order = self.club_two['order']

        if self.club_one_win:
            add_score = 10
            if order_changed > 0:
                # exchange the order
                MongoLadder.db(self.server_id).update_one(
                    {'_id': self.club_one['_id']},
                    {'$set': {'order': self.club_two['order']}}
                )

                MongoLadder.db(self.server_id).update_one(
                    {'_id': self.club_two['_id']},
                    {'$set': {'order': self.club_one['order']}}
                )

                # final_club_one_order = self.club_two['order']
                final_club_two_order = self.club_one['order']

                self_log = (1, (self.club_two_object.name, str(order_changed)))
                target_log = (4, (self.club_one_object.name, str(order_changed)))
            else:
                self_log = (5, (self.club_two_object.name,))
                target_log = (6, (self.club_one_object.name,))
        else:
            add_score = 5
            self_log = (2, (self.club_two_object.name,))
            target_log = (3, (self.club_one_object.name,))

        ladder_one = Ladder(self.server_id, int(self.club_one_object.id))
        ladder_one.add_score(add_score, send_notify=False)
        ladder_one.add_log(self_log, send_notify=False)

        if isinstance(self.club_two_object, Club):
            # real club
            ladder_two = Ladder(self.server_id, int(self.club_two_object.id))
            ladder_two.add_log(target_log)

        # 发送通知
        if isinstance(self.club_two_object, Club):
            d = Drop.generate(ConfigLadderRankReward.get_reward_object(final_club_two_order).package)
            n = Notification(self.server_id, int(self.club_two_object.id))
            n.add_ladder_notification(
                win=not self.club_one_win,
                from_name=self.club_one_object.name,
                current_order=final_club_two_order,
                ladder_score=d.ladder_score,
            )


class Ladder(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.fill_npc()
        self.add_self_to_ladder()

    @classmethod
    def send_rank_reward(cls, server_id):
        # TODO 不能全发，过滤死号
        for doc in MongoLadder.db(server_id).find():
            if doc['club_name']:
                # NPC
                continue

            char_id = int(doc['_id'])
            order = doc['order']

            config = ConfigLadderRankReward.get_reward_object(order)
            drop = Drop.generate(config.package)

            m = MailManager(server_id, char_id)
            m.add(
                title=config.mail_title,
                content=config.mail_content.format(order),
                attachment=drop.to_json(),
            )

    @classmethod
    def get_top_clubs(cls, server_id, amount=8):
        docs = MongoLadder.db(server_id).find().sort('order', pymongo.ASCENDING).limit(amount)
        clubs = [LadderClub(server_id, doc) for doc in docs]
        return clubs

    def fill_npc(self):
        if MongoLadder.db(self.server_id).count():
            return

        with LadderNPCLock(self.server_id).lock():
            if not MongoLadder.db(self.server_id).count():
                npcs = ConfigNPC.random_npcs(NPC_AMOUNT, league_level=1)

                docs = []
                for index, npc in enumerate(npcs):
                    doc = MongoLadder.document()
                    doc['_id'] = make_string_id()
                    doc['order'] = index + 1
                    doc['club_name'] = npc['club_name']
                    doc['club_flag'] = npc['club_flag']
                    doc['manager_name'] = npc['manager_name']
                    doc['staffs'] = npc['staffs']

                    docs.append(doc)

                MongoLadder.db(self.server_id).insert_many(docs)

    def add_self_to_ladder(self):
        if MongoLadder.db(self.server_id).find_one({'_id': str(self.char_id)}, {'_id': 1}):
            return

        with LadderLock(self.server_id).lock():
            count = MongoLadder.db(self.server_id).count()
            doc = MongoLadder.document()
            doc['_id'] = str(self.char_id)
            doc['order'] = count + 1
            doc['remained_times'] = DEFAULT_MATCH_TIMES

            MongoLadder.db(self.server_id).insert_one(doc)

        # 立即refresh一次
        self.make_refresh(send_notify=False)

    def do_refresh(self):
        order = MongoLadder.db(self.server_id).find_one({'_id': str(self.char_id)}, {'order': 1})['order']
        if order <= 6:
            order_range = [1, 2, 3, 4, 5]
        elif order <= 15:
            order_range = xrange(order - 1, order - 6, -1)
        elif order <= 29:
            order_range = xrange(order - 1, order - 10, -1)
        elif order <= 69:
            order_range = xrange(order - 1, order - 20, -1)
        elif order <= 199:
            order_range = xrange(order - 1, order - 50, -1)
        elif order <= 499:
            order_range = xrange(order - 1, order - 100, -1)
        elif order <= 999:
            order_range = xrange(order - 1, order - 200, -1)
        elif order <= 1499:
            order_range = xrange(order - 1, order - 300, -1)
        elif order <= 1999:
            order_range = xrange(order - 1, order - 500, -1)
        else:
            order_range = xrange(order - 1, 1994, -1)

        choose_orders = random.sample(order_range, 5)

        doc = MongoLadder.db(self.server_id).find({'order': {'$in': choose_orders}}, {'order': 1})
        return {d['_id']: d['order'] for d in doc}

    def make_refresh(self, send_notify=True):
        refreshed = self.do_refresh()
        MongoLadder.db(self.server_id).update_one(
            {'_id': str(self.char_id)},
            {'$set': {'refreshed': refreshed}}
        )

        if send_notify:
            self.send_notify()

    def match(self, target_id):
        if target_id == str(self.char_id):
            raise GameException(ConfigErrorMessage.get_error_id("LADDER_CANNOT_MATCH_SELF"))

        doc = MongoLadder.db(self.server_id).find_one({'_id': str(self.char_id)})
        if target_id not in doc['refreshed']:
            raise GameException(ConfigErrorMessage.get_error_id("LADDER_TARGET_NOT_EXIST"))

        target = MongoLadder.db(self.server_id).find_one({'_id': target_id}, {'order': 1})
        if target['order'] != doc['refreshed'][target_id]:
            raise GameException(ConfigErrorMessage.get_error_id("LADDER_TARGET_ORDER_CHANGED"))

        msg = None
        self_lock_key = 'ladder_match_{0}'.format(self.char_id)
        target_lock_key = 'ladder_match_{0}'.format(target_id)

        try:
            with Lock(self.server_id).lock(timeout=2, key=self_lock_key):
                try:
                    with Lock(self.server_id).lock(timeout=2, key=target_lock_key):
                        club_one = MongoLadder.db(self.server_id).find_one({'_id': str(self.char_id)})
                        club_two = MongoLadder.db(self.server_id).find_one({'_id': str(target_id)})

                        match = LadderMatch(self.server_id, club_one, club_two)
                        msg = match.start()

                except LockTimeOut:
                    raise GameException(ConfigErrorMessage.get_error_id("LADDER_TARGET_IN_MATCH"))
        except LockTimeOut:
            raise GameException(ConfigErrorMessage.get_error_id("LADDER_SELF_IN_MATCH"))

        self.make_refresh()
        return msg

    def add_score(self, score, send_notify=True):
        lock_key = "ladder_add_score_{0}".format(self.char_id)

        with Lock(self.server_id).lock(key=lock_key):
            doc = MongoLadder.db(self.server_id).find_one({'_id': str(self.char_id)}, {'score': 1})
            new_score = doc['score'] + score
            if new_score > 1000000:
                new_score = 1000000

            MongoLadder.db(self.server_id).update_one(
                {'_id': str(self.char_id)},
                {'$set': {'score': new_score}}
            )

        if send_notify:
            self.send_notify()


    def add_log(self, log, send_notify=True):
        MongoLadder.db(self.server_id).update_one(
            {'_id': str(self.char_id)},
            {'$push': {'logs': {
                '$each': [log],
                '$slice': -LADDER_LOG_MAX_AMOUNT
            }}},
        )

        if send_notify:
            self.send_notify()

    def send_notify(self):
        doc = MongoLadder.db(self.server_id).find_one({'_id': str(self.char_id)})

        notify = LadderNotify()
        notify.remained_times = doc['remained_times']
        notify.my_order = doc['order']
        notify.my_score = doc['score']

        refreshed = doc['refreshed']
        refreshed_docs = MongoLadder.db(self.server_id).find({'_id': {'$in': refreshed.keys()}})
        refreshed_docs = {d['_id']: d for d in refreshed_docs}

        for k, v in refreshed.iteritems():
            this_ladder_club = refreshed_docs[k]

            notify_club = notify.clubs.add()
            notify_club.id = k
            notify_club.order = v
            # TODO
            notify_club.power = 999
            notify_club.score = this_ladder_club['score']

            ladder_club = LadderClub(self.server_id, this_ladder_club)
            notify_club.name = ladder_club.name
            notify_club.flag = ladder_club.flag

        for template_id, args in doc['logs']:
            notify_log = notify.logs.add()
            notify_log.template_id = template_id
            notify_log.args.extend(args)

        MessagePipe(self.char_id).put(msg=notify)


class LadderStore(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.items = CommonLadderStore.get(self.server_id)
        if not self.items:
            self.refresh()

        Ladder(self.server_id, self.char_id)

    def refresh(self):
        with LadderStoreLock(self.server_id).lock():
            self.items = CommonLadderStore.get(self.server_id)
            if self.items:
                return

            self.items = random.sample(ConfigLadderScoreStore.INSTANCES.keys(), 9)
            CommonLadderStore.set(self.server_id, self.items)

    def buy(self, item_id):
        if item_id not in self.items:
            raise GameException(ConfigErrorMessage.get_error_id("LADDER_STORE_ITEM_NOT_EXIST"))

        doc = MongoLadder.db(self.server_id).find_one(
            {'_id': str(self.char_id)},
            {'buy_times': 1, 'score': 1}
        )

        config = ConfigLadderScoreStore.get(item_id)
        if config.times_limit == 0:
            raise GameException(ConfigErrorMessage.get_error_id("LADDER_SCORE_CANNOT_BUY"))

        if config.times_limit > 0:
            # has limit
            if doc.get('buy_times', {}).get(str(item_id), 0) >= config.times_limit:
                raise GameException(ConfigErrorMessage.get_error_id("LADDER_STORE_ITEM_REACH_LIMIT"))

        if doc['score'] < config.score:
            raise GameException(ConfigErrorMessage.get_error_id("LADDER_SCORE_NOT_ENOUGH"))

        MongoLadder.db(self.server_id).update_one(
            {'_id': str(self.char_id)},
            {
                '$inc': {
                    'buy_times.{0}'.format(item_id): 1,
                    'score': -config.score
                },
            }
        )

        drop = Drop.generate(ConfigLadderScoreStore.get(item_id).package)
        message = "Buy from ladder store. item id {0}".format(item_id)
        Resource(self.server_id, self.char_id).save_drop(drop, message=message)
        Ladder(self.server_id, self.char_id).send_notify()

    def send_notify(self):
        next_day = arrow.utcnow().replace(days=1)
        next_time = arrow.Arrow(next_day.year, next_day.month, next_day.day).timestamp

        notify = LadderStoreNotify()
        notify.next_refresh_time = next_time
        notify.ids.extend(self.items)

        MessagePipe(self.char_id).put(msg=notify)
