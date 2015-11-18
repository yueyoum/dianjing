# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       game
Date Created:   2015-11-10 15:52
Description:

"""

import arrow
import base64
from django.conf import settings

from dianjing.exception import GameException

from core.mongo import MongoCharacter, MongoLeagueGroup, MongoLeagueEvent
from core.character import Character
from core.club import Club
from core.league.group import LeagueGroup
from core.league.match import LeagueMatch, LeagueClub
from core.notification import Notification

from utils.message import MessagePipe, MessageFactory

from config.settings import LEAGUE_START_TIME_ONE, LEAGUE_START_TIME_TWO
from config import ConfigErrorMessage, ConfigLeague

from protomsg.league_pb2 import LeagueNotify


def time_string_to_datetime(day_text, time_text):
    text = "%s %s" % (day_text, time_text)
    return arrow.get(text, "YYYY-MM-DD HH:mm:ssZ").to(settings.TIME_ZONE)


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

        # 因为启动定时任务后要从这里判断改打哪一场，所以这里延时1分钟，否则可能会判断到下一场
        time_one = time_string_to_datetime(now_day_text, LEAGUE_START_TIME_ONE).replace(minutes=1)
        if now <= time_one:
            return passed_order + 1

        time_two = time_string_to_datetime(now_day_text, LEAGUE_START_TIME_TWO).replace(minutes=1)
        if now <= time_two:
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
        MongoCharacter.db(server_id).update_many(
            {},
            {'$unset': {'league_group': 1}}
        )

        MongoLeagueGroup.db(server_id).drop()
        MongoLeagueEvent.db(server_id).drop()

    @staticmethod
    def new(server_id):
        # 分组，确定一周的联赛
        LeagueGame.clean(server_id)

        for i in range(ConfigLeague.MIN_LEVEL, ConfigLeague.MAX_LEVEL + 1):
            char_ids = Character.get_recent_login_char_ids(server_id, recent_days=14,
                                                           other_conditions=[{'league_level': i}])
            g = LeagueGroup(server_id, i)

            for cid in char_ids:
                if not Club(server_id, cid, load_staff=False).match_staffs_ready():
                    continue

                try:
                    g.add(cid)
                except LeagueGroup.AddFinish:
                    g.finish()

                    # new group
                    g = LeagueGroup(server_id, i)

            g.finish()

    @staticmethod
    def join_already_started_league(server_id, char_id, send_notify=True):
        # 新用户都要做这个事情，把其放入联赛
        # 当这些帐号进入下一周后， 就会自动匹配
        if not Club(server_id, char_id, load_staff=False).match_staffs_ready():
            return

        league = League(server_id, char_id)
        if league.group_id and MongoLeagueGroup.exist(server_id, league.group_id):
            return

        g = LeagueGroup(server_id, league.league_level)
        g.add(char_id)
        g.finish()

        order = LeagueGame.find_order()
        for i in range(1, order):
            LeagueGame.start_match(server_id, group_ids=[g.id], order=i)

        if send_notify:
            League(server_id, char_id).send_notify()

    @staticmethod
    def start_match(server_id, group_ids=None, order=None):
        # 开始一场比赛
        if not order:
            order = LeagueGame.find_order()

        if order > 14:
            # 这种一般是在测试中才会出现的，比如周日第二场已经过去，
            # 这时候就会判断到该打第15场，显然是不对的
            return

        if group_ids:
            league_groups = MongoLeagueGroup.db(server_id).find({'_id': {'$in': group_ids}})
        else:
            league_groups = MongoLeagueGroup.db(server_id).find()

        for g in league_groups:
            group_id = g['_id']
            league_level = g['level']
            event_id = g['events'][order - 1]
            clubs = g['clubs']
            """:type: dict[str, dict]"""

            matchs = []
            """:type: list[LeagueMatch]"""

            club_objects = {k: LeagueClub(server_id, group_id, league_level, v) for k, v in clubs.iteritems()}
            """:type: dict[str, core.league.match.LeagueNPCClub | core.league.match.LeagueRealClub]"""

            league_event = MongoLeagueEvent.db(server_id).find_one({'_id': event_id})
            pairs = league_event['pairs']

            for k, v in pairs.iteritems():
                club_one_id = v['club_one']
                club_two_id = v['club_two']

                match = LeagueMatch(server_id, club_objects[club_one_id], club_objects[club_two_id])
                msg = match.start()

                pairs[k]['club_one_win'] = msg.club_one_win
                pairs[k]['log'] = base64.b64encode(msg.SerializeToString())
                pairs[k]['points'] = match.points

                matchs.append(match)

            group_clubs_updater = {}
            for k, v in club_objects.iteritems():
                group_clubs_updater["clubs.{0}.match_times".format(k)] = v.match_times
                group_clubs_updater["clubs.{0}.win_times".format(k)] = v.win_times
                group_clubs_updater["clubs.{0}.score".format(k)] = v.score

            event_pairs_updater = {"finished": True}
            for k, v in pairs.iteritems():
                event_pairs_updater["pairs.{0}.club_one_win".format(k)] = v['club_one_win']
                event_pairs_updater["pairs.{0}.log".format(k)] = v['log']
                event_pairs_updater["pairs.{0}.points".format(k)] = v['points']

            # 更新小组中 clubs 的信息
            MongoLeagueGroup.db(server_id).update_one(
                {'_id': group_id},
                {'$set': group_clubs_updater}
            )

            # 更新这场比赛(event) 中的pairs信息
            MongoLeagueEvent.db(server_id).update_one(
                {'_id': event_id},
                {'$set': event_pairs_updater}
            )

            club_orders = [(k, v.score) for k, v in club_objects.iteritems()]
            club_orders.sort(key=lambda item: item[1], reverse=True)
            club_orders = [k for k, v in club_orders]

            # 发送通知
            for m in matchs:
                if isinstance(m.club_one_object, Club):
                    n = Notification(server_id, int(m.club_one_object.id))
                    n.add_league_notification(
                        win=m.club_one_win,
                        target=m.club_two_object.name,
                        score_got=m.club_one_object.score_change,
                        gold_got=m.club_one_object.got_gold,
                        score_rank=club_orders.index(str(m.club_one_object.id)) + 1
                    )

                if isinstance(m.club_two_object, Club):
                    n = Notification(server_id, int(m.club_two_object.id))
                    n.add_league_notification(
                        win=not m.club_one_win,
                        target=m.club_one_object.name,
                        score_got=m.club_two_object.score_change,
                        gold_got=m.club_two_object.got_gold,
                        score_rank=club_orders.index(str(m.club_two_object.id)) + 1
                    )

            # 进阶
            if order == 14:
                # 最后一场
                for club in club_objects.values():
                    club.send_week_mail()

                club_objects[club_orders[0]].league_level_up()
                club_objects[club_orders[1]].league_level_up()

            notify = League.make_notify(server_id, group_id)
            notify_data = MessageFactory.pack(notify)
            for club in club_objects.values():
                if isinstance(club, Club):
                    MessagePipe(club.char_id).put(data=notify_data)


class League(object):
    __slots__ = ['server_id', 'char_id', 'group_id', 'league_level']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        doc = MongoCharacter.db(server_id).find_one({'_id': self.char_id}, {'league_group': 1, 'league_level': 1})
        self.group_id = doc.get('league_group', "")
        self.league_level = doc.get('league_level', 1)

    def get_statistics(self, club_id):
        if ':' in club_id:
            # npc
            group_id, club_id = club_id.split(':')
        else:
            group_id = self.group_id
            club_id = club_id

        league_group = MongoLeagueGroup.db(self.server_id).find_one(
            {'_id': group_id},
            {'level': 1, 'clubs.{0}'.format(club_id): 1}
        )

        if not league_group or club_id not in league_group['clubs']:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        club_info = league_group['clubs'][club_id]
        lc = LeagueClub(self.server_id, self.group_id, league_group['level'], club_info)

        return lc.get_match_staffs_winning_rate()

    def get_log(self, league_pair_id):
        event_id, pair_id = league_pair_id.split(':')

        league_event = MongoLeagueEvent.db(self.server_id).find_one(
            {'_id': event_id},
            {'pairs.{0}.log'.format(pair_id): 1}
        )

        if not league_event or pair_id not in league_event['pairs']:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        log = league_event['pairs'][pair_id]['log']
        if not log:
            raise GameException(ConfigErrorMessage.get_error_id("LEAGUE_NO_LOG"))

        return base64.b64decode(log)

    @staticmethod
    def make_notify(server_id, group_id):
        league_group = MongoLeagueGroup.db(server_id).find_one({'_id': group_id})
        league_events = MongoLeagueEvent.db(server_id).find({'_id': {'$in': league_group['events']}})

        events = {e['_id']: e for e in league_events}

        notify = LeagueNotify()
        notify.league.level = league_group['level']
        notify.league.current_order = LeagueGame.find_order()

        rank_info = []
        clubs_id_table = {}

        # clubs
        for k, v in league_group['clubs'].iteritems():
            notify_club = notify.league.clubs.add()
            lc = LeagueClub(server_id, group_id, league_group['level'], v)
            notify_club.MergeFrom(lc.make_protomsg())

            if not v['match_times']:
                winning_rate = 0
            else:
                winning_rate = int(v['win_times'] * 1.0 / v['match_times'] * 100)

            rank_info.append((str(lc.id), v['match_times'], v['score'], winning_rate))
            clubs_id_table[k] = str(lc.id)

        rank_info.sort(key=lambda item: -item[3])

        # ranks
        for club_id, match_times, score, winning_rate in rank_info:
            notify_rank = notify.league.ranks.add()
            notify_rank.club_id = club_id
            notify_rank.battle_times = match_times
            notify_rank.score = score
            notify_rank.winning_rate = winning_rate

        # events
        for event_id in league_group['events']:
            e = events[event_id]

            notify_event = notify.league.events.add()
            notify_event.battle_at = e['start_at']
            notify_event.finished = e['finished']

            for k, v in e['pairs'].iteritems():
                notify_event_pair = notify_event.pairs.add()
                notify_event_pair.pair_id = "{0}:{1}".format(event_id, k)
                notify_event_pair.club_one_id = clubs_id_table[v['club_one']]
                notify_event_pair.club_two_id = clubs_id_table[v['club_two']]
                notify_event_pair.club_one_win = v['club_one_win']
                notify_event_pair.points.extend(v['points'])

        return notify

    def send_notify(self):
        if not self.group_id:
            return

        notify = League.make_notify(self.server_id, self.group_id)
        MessagePipe(self.char_id).put(msg=notify)
