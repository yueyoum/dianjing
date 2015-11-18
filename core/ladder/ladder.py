# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       ladder
Date Created:   2015-11-12 16:01
Description:

"""

import random

import pymongo
from dianjing.exception import GameException
from core.mongo import MongoLadder
from core.character import Character
from core.package import Drop
from core.mail import MailManager
from core.lock import Lock, LadderLock, LadderNPCLock, LockTimeOut
from core.ladder.match import LadderClub, LadderMatch

from utils.functional import make_string_id
from utils.message import MessagePipe
from config import (
    ConfigLadderRankReward,
    ConfigNPC,
    ConfigErrorMessage,
)
from config.settings import LADDER_LOG_MAX_AMOUNT, LADDER_NPC_AMOUNT, LADDER_DEFAULT_MATCH_TIMES, LADDER_MAX_SCORE
from protomsg.ladder_pb2 import LadderNotify


class Ladder(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.fill_npc()
        self.add_self_to_ladder()

    @classmethod
    def cronjob(cls, server_id):
        # 每天按照排名发送奖励
        char_ids = Character.get_recent_login_char_ids(server_id)
        for cid in char_ids:
            doc = MongoLadder.db(server_id).find_one({'_id': cid}, {'order': 1})
            if not doc:
                continue

            order = doc['order']

            config = ConfigLadderRankReward.get_reward_object(order)
            drop = Drop.generate(config.package)

            m = MailManager(server_id, cid)
            m.add(
                title=config.mail_title,
                content=config.mail_content.format(order),
                attachment=drop.to_json(),
            )

    @classmethod
    def get_top_clubs(cls, server_id, amount=8):
        """

        :rtype : list[core.ladder.match.LadderClub]
        """
        docs = MongoLadder.db(server_id).find().sort('order', pymongo.ASCENDING).limit(amount)
        clubs = [LadderClub(server_id, doc) for doc in docs]
        return clubs

    def fill_npc(self):
        if MongoLadder.db(self.server_id).count():
            return

        with LadderNPCLock(self.server_id).lock():
            if MongoLadder.db(self.server_id).count():
                return

            npcs = ConfigNPC.random_npcs(LADDER_NPC_AMOUNT, league_level=1)

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
            doc['remained_times'] = LADDER_DEFAULT_MATCH_TIMES

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
        drop = Drop()
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
                        drop.ladder_score = match.club_one_add_score

                except LockTimeOut:
                    raise GameException(ConfigErrorMessage.get_error_id("LADDER_TARGET_IN_MATCH"))
        except LockTimeOut:
            raise GameException(ConfigErrorMessage.get_error_id("LADDER_SELF_IN_MATCH"))

        self.make_refresh()
        return msg, drop.make_protomsg()

    def add_score(self, score, send_notify=True):
        lock_key = "ladder_add_score_{0}".format(self.char_id)

        with Lock(self.server_id).lock(key=lock_key):
            doc = MongoLadder.db(self.server_id).find_one({'_id': str(self.char_id)}, {'score': 1})
            new_score = doc['score'] + score
            if new_score > LADDER_MAX_SCORE:
                new_score = LADDER_MAX_SCORE

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
