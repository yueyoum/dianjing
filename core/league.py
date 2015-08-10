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
import base64

import arrow

from django.conf import settings

from dianjing.exception import GameException

from core.db import MongoDB
from core.mongo import Document
from core.club import Club
from core.match import ClubMatch
from core.abstract import AbstractClub, AbstractStaff

from config.settings import LEAGUE_START_TIME_ONE, LEAGUE_START_TIME_TWO
from config import ConfigNPC, ConfigStaff, ConfigErrorMessage

from utils.message import MessagePipe

from protomsg.league_pb2 import LeagueNotify


GROUP_CLUBS_AMOUNT = 14
GROUP_MAX_REAL_CLUBS_AMOUNT = 12

ARROW_FORMAT = "YYYY-MM-DD HH:mm:ssZ"


def time_string_to_datetime(day_text, time_text):
    text = "%s %s" % (day_text, time_text)
    return arrow.get(text).to(settings.TIME_ZONE)

def make_id():
    return str(uuid.uuid4())


class LeagueNPCStaff(AbstractStaff):
    def __init__(self, staff_attribute):
        super(LeagueNPCStaff, self).__init__()

        self.id = staff_attribute['id']
        config = ConfigStaff.get(self.id)

        # TODO
        self.level = 1
        self.race = config.race

        self.jingong = staff_attribute['jingong']
        self.qianzhi = staff_attribute['qianzhi']
        self.xintai = staff_attribute['xintai']
        self.baobing = staff_attribute['baobing']
        self.fangshou = staff_attribute['fangshou']
        self.yunying = staff_attribute['yunying']
        self.yishi = staff_attribute['yishi']
        self.caozuo = staff_attribute['caozuo']

        skill_level = staff_attribute.get('skill_level', 1)
        self.skills = {i: skill_level for i in config.skill_ids}


class LeagueNPCClub(AbstractClub):
    def __init__(self, club_name, manager_name, staffs):
        super(LeagueNPCClub, self).__init__()

        self.id = 0
        self.name = club_name
        self.manager_name = manager_name
        # TODO
        self.flag = 1
        self.policy = 1

        for s in staffs:
            self.match_staffs.append(s['id'])
            self.staffs[s['id']] = LeagueNPCStaff(s)



class LeagueClub(object):
    def __new__(cls, server_id, club):
        # club 是存在mongo中的数据
        if club['club_id']:
            return Club(server_id, club['club_id'])

        return LeagueNPCClub(club['club_name'], club['manager_name'], club['staffs'])



class LeagueMatch(object):
    # 一对俱乐部比赛
    def __init__(self, server_id, club_one, club_two):
        # club_one, club_two 是存在mongodb中的数据
        self.server_id = server_id
        self.club_one = club_one
        self.club_two = club_two

    def start(self):
        club_one = LeagueClub(self.server_id, self.club_one)
        club_two = LeagueClub(self.server_id, self.club_two)

        match = ClubMatch(club_one, club_two)
        msg = match.start()

        self.club_one['match_times'] += 1
        self.club_two['match_times'] += 1


        if msg.club_one_win:
            self.club_one['win_times'] += 1
        else:
            self.club_two['win_times'] += 1

        # TODO score

        return msg



class LeagueGame(object):
    # 每周的联赛

    @staticmethod
    def find_order():
        # 确定当前应该打第几场
        now = arrow.utcnow().to(settings.TIME_ZONE)
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
        # 根据场次返回开始时间
        now = arrow.utcnow().to(settings.TIME_ZONE)

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

        date_text = "{0} {1}".format(
            now.replace(days=change_days).format("YYYY-MM-DD"),
            time_text
        )

        return arrow.get(date_text).replace(tzinfo=settings.TIME_ZONE)



    @staticmethod
    def clean(server_id):
        mongo = MongoDB.get(server_id)

        mongo.character.update_many({}, {"$unset": {"league_group": 1}})
        mongo.league_group.drop()
        mongo.league_event.drop()


    @staticmethod
    def new(server_id):
        # 分组，确定一周的联赛
        LeagueGame.clean(server_id)

        # TODO 分组级别
        # TODO 死号
        # TODO 如何根据server_id来将定时任务分配到多台机器上

        mongo = MongoDB.get(server_id)
        # TODO 判断size 是否要建立索引？
        chars = mongo.character.find({'club.match_staffs': {'$size': 5}}, {'club.match_staffs': 1})

        # TODO league level
        g = LeagueGroup(server_id, 1)

        for c in chars:
            if 0 in c['club']['match_staffs']:
                continue

            try:
                g.add(c['_id'])
            except LeagueGroup.ClubAddFinish:
                g.finish()

                # new group
                g = LeagueGroup(server_id, 1)

        g.finish()


    @staticmethod
    def join_already_started_league(server_id, club_id):
        # 每周的新用户都要做这个事情，把其放入联赛
        # 当这些帐号进入下一周后， 就会 自动匹配
        g = LeagueGroup(server_id, 1)
        g.add(club_id)
        g.finish()

        LeagueGame.start_match(server_id, group_ids=[g.id])
        League(server_id, club_id).send_notify()


    @staticmethod
    def start_match(server_id, group_ids=None, order=None):
        # 开始一场比赛
        mongo = MongoDB.get(server_id)

        if not order:
            order = LeagueGame.find_order()

        if group_ids:
            league_groups = mongo.league_group.find({'_id': {'$in': group_ids}})
        else:
            league_groups = mongo.league_group.find()

        for g in league_groups:
            event_id = g['events'][order]

            clubs = g['clubs']

            league_event = mongo.league_event.find_one({'_id': event_id})
            pairs = league_event['pairs']

            for k, v in pairs.iteritems():
                club_one_id = v['club_one']
                club_two_id = v['club_two']

                club_one = clubs[ club_one_id ]
                club_two = clubs[ club_two_id ]

                match = LeagueMatch(server_id, club_one, club_two)
                msg = match.start()

                pairs[k]['club_one_win'] = msg.club_one_win
                pairs[k]['log'] = base64.b64encode(msg.SerializeToString())

            group_clubs_updater = {}
            for k, v in clubs.iteritems():
                group_clubs_updater["clubs.{0}.match_times".format(k)] = v['match_times']
                group_clubs_updater["clubs.{0}.win_times".format(k)] = v['win_times']
                group_clubs_updater["clubs.{0}.score".format(k)] = v['score']


            event_pairs_updater = {}
            event_pairs_updater["finished"] = True
            for k, v in pairs.iteritems():
                event_pairs_updater["pairs.{0}.club_one_win".format(k)] = v['club_one_win']
                event_pairs_updater["pairs.{0}.log".format(k)] = v['log']

            # 更新小组中 clubs 的信息
            mongo.league_group.update_one(
                {'_id': g['_id']},
                {'$set': group_clubs_updater}
            )

            # 更新这场比赛(event) 中的pairs信息
            mongo.league_event.update_one(
                {'_id': event_id},
                {'$set': event_pairs_updater}
            )



class LeagueGroup(object):
    # 一个分组

    class ClubAddFinish(Exception):
        pass

    def __init__(self, server_id, level):
        self.id = make_id()

        self.server_id = server_id
        self.level = level
        self.mongo = MongoDB.get(server_id)

        self.real_clubs = []
        self.all_clubs = {}

        self.event_docs = []

    @property
    def event_ids(self):
        return [e['_id'] for e in self.event_docs]


    def add(self, club_id):
        self.real_clubs.append(club_id)

        if len(self.real_clubs) >= GROUP_MAX_REAL_CLUBS_AMOUNT:
            raise LeagueGroup.ClubAddFinish()


    def finish(self):
        if not self.real_clubs:
            return


        def make_real_club_doc(club_id):
            club = Document.get("league.club")
            club['club_id'] = club_id
            return club


        def make_npc_club_doc(npc):
            """

            :type npc: config.npc.NPC
            """
            club = Document.get("league.club")
            club['club_id'] = 0

            club['club_name'] = npc.name
            club['manager_name'] = npc.manager_name

            staffs = []
            staff_ids = ConfigStaff.random_ids(5)
            for i in range(5):
                staffs.append({
                    'id': staff_ids[i],
                    'jingong': random.randint(npc.jingong_low, npc.jingong_high) * self.level,
                    'qianzhi': random.randint(npc.qianzhi_low, npc.qianzhi_high) * self.level,
                    'xintai': random.randint(npc.xintai_low, npc.xintai_high) * self.level,
                    'baobing': random.randint(npc.baobing_low, npc.baobing_high) * self.level,
                    'fangshou': random.randint(npc.fangshou_low, npc.fangshou_high) * self.level,
                    'yunying': random.randint(npc.yunying_low, npc.yunying_high) * self.level,
                    'yishi': random.randint(npc.yishi_low, npc.yishi_high) * self.level,
                    'caozuo': random.randint(npc.caozuo_low, npc.caozuo_high) * self.level,
                    'skill_level': random.randint(npc.skill_low, npc.skill_high)
                })

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
            doc = Document.get("league.pair")
            doc['club_one'] = club_one
            doc['club_two'] = club_two
            return doc


        for index, event in enumerate(match):
            edoc = Document.get("league.event")
            edoc['_id'] = make_id()
            edoc['start_at'] = LeagueGame.find_match_time(index+1).format(ARROW_FORMAT)

            pair_docs = [make_pair_doc(one, two) for one, two in event]
            edoc['pairs'] = {str(i+1): pair_docs[i] for i in range(len(pair_docs))}

            self.event_docs.append(edoc)


        group_doc = Document.get("league.group")
        group_doc['_id'] = self.id
        group_doc['level'] = self.level
        group_doc['clubs'] = self.all_clubs
        group_doc['events'] = self.event_ids

        self.mongo.league_event.insert_many(self.event_docs)
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
        self.mongo = MongoDB.get(server_id)

        doc = self.mongo.character.find_one({'_id': self.char_id}, {'league_group': 1})
        self.group_id = doc.get('league_group', "")

        self.order = LeagueGame.find_order()


    def get_statistics(self, league_club_id):
        group_id, club_id = league_club_id.split(':')

        league_group = self.mongo.league_group.find_one(
            {'_id': group_id},
            {'clubs.{0}'.format(club_id): 1}
        )

        if not league_group or club_id not in league_group['clubs']:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        club_info = league_group['clubs'][club_id]

        # TODO real data
        winning_rate = {
            't': 10,
            'z': 10,
            'p': 10,
        }

        return [(i, winning_rate) for i in range(10, 16)]


    def get_log(self, league_pair_id):
        event_id, pair_id = league_pair_id.split(':')

        league_event = self.mongo.league_event.find_one(
            {'_id': event_id},
            {'pairs.{0}.log'.format(pair_id): 1}
        )

        if not league_event or pair_id not in league_event['pairs']:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        log = league_event['pairs'][pair_id]['log']
        if not log:
            raise GameException(ConfigErrorMessage.get_error_id("LEAGUE_NO_LOG"))

        return base64.b64decode(log)


    def send_notify(self):
        if not self.group_id:
            return

        league_group = self.mongo.league_group.find_one({'_id': self.group_id})
        league_events = self.mongo.league_event.find({'_id': {'$in': league_group['events']}})

        events = {e['_id']: e for e in league_events}

        notify = LeagueNotify()
        notify.league.level = league_group['level']
        notify.league.current_order = LeagueGame.find_order()


        rank_info = []

        # clubs
        for k, v in league_group['clubs'].iteritems():
            league_club_id = "{0}:{1}".format(self.group_id, k)

            notify_club = notify.league.clubs.add()
            notify_club.league_club_id = league_club_id
            notify_club.club.MergeFrom( LeagueClub(self.server_id, v).make_protomsg() )

            rank_info.append( (league_club_id, v['match_times'], v['win_times'], v['score']) )

        # ranks
        # TODO rank sort
        for league_club_id, match_times, win_times, score in rank_info:
            notify_rank = notify.league.ranks.add()

            notify_rank.league_club_id = league_club_id
            notify_rank.battle_times = match_times
            notify_rank.score = score

            if match_times:
                notify_rank.winning_rate = int(win_times * 1.0 / match_times * 100)
            else:
                notify_rank.winning_rate = 0

        # events
        for event_id in league_group['events']:
            e = events[event_id]

            notify_event = notify.league.events.add()
            notify_event.battle_at = arrow.get(e['start_at'], ARROW_FORMAT).timestamp
            notify_event.finished = e['finished']

            for k, v in e['pairs'].iteritems():
                notify_event_pair = notify_event.pairs.add()
                notify_event_pair.pair_id = "{0}:{1}".format(event_id, k)
                notify_event_pair.league_club_one_id = "{0}:{1}".format(self.group_id, v['club_one'])
                notify_event_pair.league_club_two_id = "{0}:{1}".format(self.group_id, v['club_two'])
                notify_event_pair.club_one_win = v['club_one_win']


        MessagePipe(self.char_id).put(msg=notify)

