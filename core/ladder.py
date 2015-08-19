# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       ladder
Date Created:   2015-08-13 16:26
Description:

"""

import random
import pymongo

from dianjing.exception import GameException

from core.db import MongoDB
from core.mongo import Document
from core.abstract import AbstractStaff, AbstractClub
from core.club import Club
from core.match import ClubMatch

from core.lock import LadderLock, LadderNPCLock

from utils.functional import make_string_id
from utils.message import MessagePipe

from config import ConfigLadderScoreStore, ConfigLadderRankReward, ConfigNPC, ConfigErrorMessage, ConfigStaff

from protomsg.ladder_pb2 import LadderNotify


NPC_AMOUNT = 2000


class LadderNPCStaff(AbstractStaff):
    def __init__(self, data):
        super(LadderNPCStaff, self).__init__()

        # XXX
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
    def __init__(self, ladder_id, club_name, manager_name, club_flag, staffs):
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


class LadderClub(object):
    def __new__(cls, server_id, club):
        # club 是 Ladder 数据
        if club['club_name']:
            #NPC
            return LadderNPCClub(club['_id'], club['club_name'], club['manager_name'], club['club_flag'], club['staffs'])

        return Club(server_id, int(club['_id']))


class LadderMatch(object):
    def __init__(self, server_id, club_one, club_two):
        self.server_id = server_id
        self.club_one = club_one
        self.club_two = club_two

        self.club_one_win = False

    def start(self):
        club_one = LadderClub(self.server_id, self.club_one)
        club_two = LadderClub(self.server_id, self.club_two)

        match = ClubMatch(club_one, club_two)
        msg = match.start()

        self.club_one_win = msg.club_one_win
        return msg




class Ladder(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = MongoDB.get(server_id)

        self.fill_npc()
        self.add_self_to_ladder()
        self.create_index()


    def create_index(self):
        self.mongo.ladder.create_index([('order', pymongo.DESCENDING)])


    def fill_npc(self):
        if self.mongo.ladder.count():
            return

        with LadderNPCLock(self.server_id).lock():
            if not self.mongo.ladder.count():
                npcs = ConfigNPC.random_npcs(NPC_AMOUNT, league_level=1)

                docs = []
                for index, npc in enumerate(npcs):
                    doc = Document.get("ladder")
                    doc['_id'] = make_string_id()
                    doc['order'] = index+1
                    doc['club_name'] = npc['club_name']
                    doc['club_flag'] = npc['club_flag']
                    doc['manager_name'] = npc['manager_name']
                    doc['staffs'] = npc['staffs']

                    docs.append(doc)

                self.mongo.ladder.insert_many(docs)


    def add_self_to_ladder(self):
        if self.mongo.ladder.find_one({'_id': str(self.char_id)}, {'_id': 1}):
            return

        with LadderLock(self.server_id).lock():
            count = self.mongo.ladder.count()
            doc = Document.get("ladder")
            doc['_id'] = str(self.char_id)
            doc['order'] = count+1

            self.mongo.ladder.insert_one(doc)

        # 立即refresh一次
        self.make_refresh(send_notify=False)


    def refresh(self):
        order = self.mongo.ladder.find_one({'_id': str(self.char_id)}, {'order': 1})['order']
        if order <= 6:
            order_range = [1,2,3,4,5]
        elif order <= 15:
            order_range = range(order, order-6, -1)
        elif order <= 29:
            order_range = range(order, order-10, -1)
        elif order <= 69:
            order_range = range(order, order-20, -1)
        elif order <= 199:
            order_range = range(order, order-50, -1)
        elif order <= 499:
            order_range = range(order, order-100, -1)
        elif order <= 999:
            order_range = range(order, order-200, -1)
        elif order <= 1499:
            order_range = range(order, order-300, -1)
        elif order <= 1999:
            order_range = range(order, order-500, -1)
        else:
            order_range = range(order, 1995, -1)

        choose_orders = random.sample(order_range, 5)

        doc = self.mongo.ladder.find({'order': {'$in': choose_orders}}, {'order': 1})
        return {d['_id']: d['order'] for d in doc}


    def make_refresh(self, send_notify=True):
        refreshed = self.refresh()
        self.mongo.ladder.update_one(
            {'_id': str(self.char_id)},
            {'$set': {'refreshed': refreshed}}
        )

        if send_notify:
            self.send_notify()


    def match(self, target_id):
        doc = self.mongo.ladder.find_one({'_id': str(self.char_id)})
        if str(target_id) not in doc['refreshed']:
            raise GameException(ConfigErrorMessage.get_error_id("LADDER_TARGET_NOT_EXIST"))


        target = self.mongo.ladder.find_one({'_id': target_id}, {'order': 1})
        if target['order'] != doc['refreshed'][str(target_id)]:
            raise GameException(ConfigErrorMessage.get_error_id("LADDER_TARGET_ORDER_CHANGED"))

        # TODO match lock

        club_one = self.mongo.ladder.find_one({'_id': str(self.char_id)})
        club_two = self.mongo.ladder.find_one({'_id': str(target_id)})

        match = LadderMatch(self.server_id, club_one, club_two)
        msg = match.start()

        if club_one['order'] > club_two['order'] and match.club_one_win:
            # exchange the order
            self.mongo.ladder.update_one(
                {'_id': str(self.char_id)},
                {'$set': {'order': club_two['order']}}
            )

            self.mongo.ladder.update_one(
                {'_id': str(target_id)},
                {'$set': {'order': club_one['order']}}
            )

            if target_id.isdigit():
                Ladder(self.server_id, int(target_id)).send_notify()

        self.make_refresh()
        return msg


    def send_notify(self):
        doc = self.mongo.ladder.find_one({'_id': str(self.char_id)})

        notify = LadderNotify()
        # TODO
        notify.remained_times = 10
        notify.my_order = doc['order']

        refreshed = doc['refreshed']
        refreshed_docs = self.mongo.ladder.find({'_id': {'$in': refreshed.keys()}})
        refreshed_docs = {d['_id']: d for d in refreshed_docs}

        for k, v in refreshed.iteritems():
            this_ladder_club = refreshed_docs[k]

            notify_club = notify.clubs.add()
            notify_club.id = k
            notify_club.order = v

            if this_ladder_club['club_name']:
                # NPC
                notify_club.name = this_ladder_club['club_name']
                notify_club.flag = this_ladder_club['club_flag']
            else:
                # REAL club
                club = Club(self.server_id, self.char_id)
                notify_club.name = club.name
                notify_club.flag = club.flag

        for template_id, args in doc['logs']:
            notify_log = notify.logs.add()
            notify_log.template_id = template_id
            notify_log.args.extend(args)

        MessagePipe(self.char_id).put(msg=notify)


