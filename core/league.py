# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       league
Date Created:   2015-07-22 10:41
Description:

"""


#                                      +------------+
#                                      | LeagueGame |  每周开始新的联赛
#                                      +------------+
#                                            |
#                  +-----------------------------------------------+
#                  |                                               |
#           +-------------+                                    +-------------+
#           | LeagueGroup |                                    | LeagueGroup |
#           +-------------+                                    +-------------+
#           |  小组 #1     |                                    |   小组 #N    |
#           +-------------+                                    +-------------+
#                  |                                                 |
#      +--------------------------+                     +------------------------+
#      |                          |                     |                        |
# +--------------+    ...  +--------------+     +--------------+    ...   +--------------+
# | LeagueEvent  |         | LeagueEvent  |     | LeagueEvent  |          | LeagueEvent  |
# +--------------+         +--------------+     +--------------+          +--------------+
# | 一次比赛 #1   |         | 一次比赛 #14   |     | 一次比赛 #1   |          | 一次比赛 #14   |
# +--------------+         +--------------+     +--------------+          +--------------+
#       |
# +--------------+
# | LeaguePair   |
# +--------------+          ......
# |   7对俱乐部   |
# +--------------+
#
#
# 一场联赛是由很多小组赛组成的 Group
# 小组根据俱乐部等级分组
# 每个小组有14支俱乐部 （包括NPC）
# 这14支俱乐部每天要参与两场比赛，每个俱乐部与另外两个比赛，每天都和不同的比
# 每天 定时开启两次比赛
# 每天该开始哪场比赛由 LeagueGame 中的 find_order 确定
# 每周刷新的时候直接清空以前的记录，并生成新记录

import uuid
import random

import arrow

from django.conf import settings

from core.db import get_mongo_db
from core.mongo import Document

from config.settings import LEAGUE_START_TIME_ONE, LEAGUE_START_TIME_TWO
from config.npc import ConfigNPC

from utils.message import MessagePipe

from protomsg.league_pb2 import LeagueNotify

TIME_ZONE = settings.TIME_ZONE

GROUP_CLUBS_AMOUNT = 14
GROUP_MAX_REAL_CLUBS_AMOUNT = 12


def time_string_to_datetime(day_text, time_text):
    text = "%s %s" % (day_text, time_text)
    return arrow.get(text).to(TIME_ZONE)

def make_id():
    return str(uuid.uuid4())


class LeagueGame(object):
    # 每周的联赛
    @staticmethod
    def find_order():
        now = arrow.utcnow().to(TIME_ZONE)
        now_day_text = now.format("YYYY-MM-DD")

        weekday = now.weekday()
        passed_days = weekday - 0
        passed_order = passed_days * 2

        time_one = time_string_to_datetime(now_day_text, LEAGUE_START_TIME_ONE)
        if now < time_one:
            return passed_order + 1

        time_two = time_string_to_datetime(now_day_text, LEAGUE_START_TIME_TWO)
        if now < time_two:
            return passed_order + 2

        return passed_order + 3

    @staticmethod
    def find_match_time(order):
        now = arrow.utcnow().to(TIME_ZONE)

        # 一天打两次
        days, rest = divmod(order, 2)

        # 调整天数
        # 0 是周一
        change_days = 0 - now.weekday() + days

        if rest == 0:
            # order 为 2,4,6,8,10,12,14的情况
            # 应该要打当天第二场
            # 此时 days 分别为 1,2,3...7
            # 但因为是当天第二场，所以
            change_days -= 1
            time_text = LEAGUE_START_TIME_TWO
        else:
            # order 为 1,3,5,7,9,11,13的情况
            # 此时 days, rest 分别为 (0,1), (1,1), (2,1)...
            # 也就是当天/第二天第一场
            time_text = LEAGUE_START_TIME_ONE

        date_text = "{0} {1}+08:00".format(
            now.replace(days=change_days).format("YYYY-MM-DD"),
            time_text
        )

        return arrow.get(date_text)



    @staticmethod
    def clean(server_id):
        mongo = get_mongo_db(server_id)

        mongo.league_group.drop()
        mongo.league_event.drop()



    @staticmethod
    def new(server_id):
        LeagueGame.clean(server_id)

        # TODO 分组级别
        # TODO 死号
        # TODO 如何根据server_id来将定时任务分配到多台机器上

        mongo = get_mongo_db(server_id)
        chars = mongo.character.find({}, {'_id': 1})

        g = LeagueGroup(server_id, 1)

        for c in chars:
            try:
                g.add(c['_id'])
            except LeagueGroup.ClubAddFinish:
                g.finish()

                # new group
                g = LeagueGroup(server_id, 1)

        g.finish()



class LeagueGroup(object):
    # 一个分组

    class ClubAddFinish(Exception):
        pass

    def __init__(self, server_id, level):
        self.id = make_id()

        self.server_id = server_id
        self.level = level
        self.mongo = get_mongo_db(server_id)

        self.real_clubs = []
        self.all_clubs = {}


    def add(self, club_id):
        self.real_clubs.append(club_id)

        if len(self.real_clubs) >= GROUP_MAX_REAL_CLUBS_AMOUNT:
            raise LeagueGroup.ClubAddFinish()


    def finish(self):
        if not self.real_clubs:
            return


        def make_real_club_doc(club_id):
            club = Document.get("league_club")
            club['club_id'] = club_id
            return club


        def make_npc_club_doc(npc):
            """

            :type npc: config.npc.NPC
            """
            club = Document.get("league_club")
            club['club_id'] = 0

            club['club_name'] = npc.name
            club['manager_name'] = npc.manager_name

            staffs = {
                'jingong': random.randint(npc.jingong_low, npc.jingong_high) * self.level,
                'qianzhi': random.randint(npc.qianzhi_low, npc.qianzhi_high) * self.level,
                'xintai': random.randint(npc.xintai_low, npc.xintai_high) * self.level,
                'baobing': random.randint(npc.baobing_low, npc.baobing_high) * self.level,
                'fangshou': random.randint(npc.fangshou_low, npc.fangshou_high) * self.level,
                'yunying': random.randint(npc.yunying_low, npc.yunying_high) * self.level,
                'yishi': random.randint(npc.yishi_low, npc.yishi_high) * self.level,
                'caozuo': random.randint(npc.caozuo_low, npc.caozuo_high) * self.level,
            }

            club['staffs'] = staffs
            return club


        clubs = [make_real_club_doc(i) for i in self.real_clubs]

        need_npc_amount = GROUP_CLUBS_AMOUNT - len(clubs)
        npcs = ConfigNPC.random_npcs(need_npc_amount)

        npc_clubs = [make_npc_club_doc(npc) for npc in npcs]

        clubs.extend(npc_clubs)

        self.all_clubs = {str(i+1): clubs[i] for i in range(GROUP_CLUBS_AMOUNT)}

        match = self.arrange_match(self.all_clubs.keys())

        self.save(match)


    def arrange_match(self, clubs):
        # 对小组内的14支俱乐部安排比赛
        # 算法：
        # clubs = range(1, 15)
        # match = []
        # for day in range(7):
        #     pairs = []
        #     for i in range(len(clubs)):
        #         j = i + 1 + day
        #         while j >= len(clubs):
        #             j -= len(clubs)
        #
        #         pairs.append((clubs[i], clubs[j]))
        #
        #     random.shuffle(pairs)
        #     match.append(pairs[:len(clubs)/2])
        #     match.append(pairs[len(clubs)/2:])
        #
        # result format:
        # [
        #     [ (1,2), (2,3)... ], 7 pairs
        #     [ ] ...
        #     14 list
        # ]


        random.shuffle(clubs)

        match = []
        for day in range(7):
            pairs = []
            for i in range(GROUP_CLUBS_AMOUNT):
                j = i + 1 + day
                while j >= GROUP_CLUBS_AMOUNT:
                    j -= GROUP_CLUBS_AMOUNT

                pairs.append((clubs[i], clubs[j]))

            random.shuffle(pairs)

            match.append( pairs[:GROUP_CLUBS_AMOUNT/2] )
            match.append( pairs[GROUP_CLUBS_AMOUNT/2:] )

        return match


    def save(self, match):

        def make_pair_doc(club_one, club_two):
            doc = Document.get("league_pair")
            doc['club_one'] = club_one
            doc['club_two'] = club_two
            return doc

        group_events = []
        event_docs = []

        for index, event in enumerate(match):
            edoc = Document.get("league_event")
            edoc['_id'] = make_id()
            edoc['start_at'] = LeagueGame.find_match_time(index+1).format("YYYY-MM-DD HH:mm:ssZ")

            pair_docs = [make_pair_doc(one, two) for one, two in event]
            edoc['pairs'] = {str(i+1): pair_docs[i] for i in range(len(pair_docs))}

            event_docs.append(edoc)
            group_events.append(edoc['_id'])


        group_doc = Document.get("league_group")
        group_doc['_id'] = self.id
        group_doc['level'] = self.level
        group_doc['clubs'] = self.all_clubs
        group_doc['events'] = group_events

        self.mongo.league_event.insert_many(event_docs)
        self.mongo.league_group.insert_one(group_doc)

        # 然后将 此 group_id 关联到 character中
        self.mongo.character.update_many(
            {'_id': {'$in': self.real_clubs}},
            {'$set': {'league_group': self.id}}
        )


class League(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = get_mongo_db(server_id)

        char = self.mongo.character.find_one({'_id': self.char_id}, {'league_group': 1})
        group_id = char.get('league_group', "")

        if not group_id:
            raise RuntimeError("no group...")

        self.group_id = group_id
        self.order = LeagueGame.find_order()



    def send_notify(self):
        league_group = self.mongo.league_group.find_one({'_id': self.group_id})
        league_events = self.mongo.league_event.find({'_id': {'$in': league_group['events']}})

        events = {e['_id']: e for e in league_events}

        # 将club信息缓存在这里，方便后续查找
        clubs = {}

        notify = LeagueNotify()
        notify.league.level = league_group['level']
        notify.league.current_order = LeagueGame.find_order()

        # ranks
        for k, v in league_group['clubs'].iteritems():
            league_club_id = "{0}:{1}".format(self.group_id, k)
            if v['club_id']:
                # real club
                char = self.mongo.character.find_one({'_id': v['club_id']}, {'club.name': 1})
                name = char['club']['name']
            else:
                name = v['club_name']

            notify_rank = notify.league.ranks.add()
            notify_rank.id = league_club_id
            notify_rank.name = name
            notify_rank.battle_times = v['match_times']
            notify_rank.score = v['score']

            if v['match_times']:
                notify_rank.winning_rate = int(v['win_times'] * 1.0 / v['match_times'] * 100)
            else:
                notify_rank.winning_rate = 0

            clubs[k] = {
                'league_club_id': league_club_id,
                'name': name
            }


        def _set_msg_pair_club(msg_club, club_internal_id, club_win):
            msg_club.id = clubs[ str(club_internal_id) ]['league_club_id']
            msg_club.name = clubs[ str(club_internal_id) ]['name']
            msg_club.win = club_win

        # pairs
        for event_id in league_group['events']:
            e = events[event_id]

            for k, v in e['pairs'].iteritems():
                notify_pair = notify.league.pairs.add()
                notify_pair.pair_id = "{0}:{1}".format(event_id, k)
                notify_pair.battle_at = arrow.get(e['start_at']).timestamp

                _set_msg_pair_club(notify_pair.club_one, v['club_one'], v['club_one_win'])
                _set_msg_pair_club(notify_pair.club_two, v['club_two'], not v['club_one_win'])

        MessagePipe(self.char_id).put(msg=notify)

