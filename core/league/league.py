# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       game
Date Created:   2015-11-10 15:52
Description:

"""
import arrow

from dianjing.exception import GameException

from core.resource import Resource
from core.mongo import MongoLeague
from core.package import Drop
from core.match import ClubMatch
from core.club import Club
from core.staff import StaffManger

from config.league import ConfigLeague
from config.errormsg import ConfigErrorMessage

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.league_pb2 import LeagueUserNotify, LeagueCLubNotify

from utils.message import MessagePipe


MAX_CHALLENGE_TIMES = 7
MAX_MATCH_CLUB = 6

REFRESH_DIAMOND_COST = 200
REFRESH_TYPE_NORMAL = 1
REFRESH_TYPE_DIAMOND = 2

RISE_IN_RANK_FAIL_PUNISH = 300

CHALLENGE_WIN_GET_SCORE = 3
CHALLENGE_LOST_GET_SCORE = 0
DEFENCE_WIN_GET_SCORE = 0
DEFENCE_LOST_GET_SCORE = -3


class LeagueClub(object):
    def __init__(self, server_id, char_id):
        doc = MongoLeague.db(server_id).find_one({'_id': char_id})
        self._id = char_id
        self.score = doc['score']
        self.level = doc['level']
        self.daily_reward = doc['daily_reward']
        self.times = doc['times']
        self.win_rate = doc['win_rate']
        self.in_rise = doc['in_rise']

        self.club_match = doc['club_match']


class LeagueManger(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoLeague.exist(self.server_id, self.char_id):
            doc = MongoLeague.DOCUMENT
            doc['_id'] = str(self.char_id)
            doc['times'] = MAX_CHALLENGE_TIMES
            MongoLeague.db(self.server_id).insert_one(doc)
            # first create, add match club
            self.refresh()

        # self.club = LeagueClub(self.server_id, self.char_id)

    def get_score(self):
        doc = MongoLeague.db(self.server_id).find_one({'_id': self.char_id}, {'score': 1})
        return doc['score']

    def diamond_refresh(self):
        need_diamond = REFRESH_DIAMOND_COST
        message = u"Refresh {0} League Match CLub".format(self.char_id)
        with Resource(self.server_id, self.char_id).check(need_diamond=-need_diamond, message=message):
            self.refresh()

    def refresh(self):
        """
        refresh the match_club
        """
        # check if in rise
        doc_self = MongoLeague.db(self.server_id).find_one({'_id': self.char_id}, {'in_rise': 1})
        if doc_self['in_rise']:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        updater = {}
        docs = MongoLeague.db(self.server_id).find(
            {'score': {'$gte': self.get_score()}}
        ).sort('score', 1).limit(MAX_MATCH_CLUB)

        for doc in docs:
            club = MongoLeague.MATCH_CLUB_DOCUMENT
            club['flag'] = doc['flag']
            club['name'] = doc['name']
            club['win_rate'] = doc['win_rate']
            club['score'] = doc['score']

            updater[str(doc['_id'])] = club

        if updater:
            MongoLeague.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {'match_club': updater}}
            )

            self.notify_match_club()

    def report(self, key, win_club, result):
        timestamp, club_one, club_two = str(key).split(',')
        if club_one != str(self.char_id):
            return

        StaffManger(self.server_id, self.char_id).update_winning_rate(result)
        StaffManger(self.server_id, club_two).update_winning_rate(result, False)

        if win_club == str(self.char_id):
            self.result(True, True)
            LeagueManger(self.server_id, int(club_two)).result()
        else:
            self.result(False, True)
            LeagueManger(self.server_id, int(club_two)).result(True)

    def result(self, win=False, challenger=False):
        doc = MongoLeague.db(self.server_id).find_one({'_id': self.char_id}, {'match_club': 0})
        if not doc:
            raise GameException(ConfigErrorMessage.get_error_id('BAD_MESSAGE'))

        if win:
            if challenger:
                doc['score'] += CHALLENGE_WIN_GET_SCORE
            else:
                doc['score'] += DEFENCE_WIN_GET_SCORE
        else:
            if challenger:
                doc['score'] += DEFENCE_LOST_GET_SCORE
            else:
                doc['score'] += CHALLENGE_LOST_GET_SCORE

        if doc['score'] < 0:
            doc['score'] = 0

        if doc['score'] >= 1000:
            doc['score'] = 1000
            self.rise_in_rank_match(doc['level'])

        MongoLeague.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'score': doc['score']}}
        )

        self.notify_user_info()

    def get_daily_reward(self):
        # get current daily reward
        doc = MongoLeague.db(self.server_id).find_one({'_id': self.char_id}, {'match_club': 0})

        if doc['daily_reward'] == str(arrow.now().date()):
            # already got
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        conf = ConfigLeague.get(doc['level'])
        drop = Drop().generate(conf.daily_reward)
        with Resource(self.server_id, self.char_id).save_drop(drop, message="Add League Daily Reward"):
            MongoLeague.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {"daily_reward": str(arrow.now().date())}}
            )

        return drop.make_protomsg()

    def challenge(self, club_id):
        doc = MongoLeague.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'match_club.{0}'.format(club_id): 1, 'times': 1}
        )
        # 检查是否有该挑战
        if club_id not in doc['match_club']:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))
        # 检查是否有挑战次数
        if doc['times'] < 1:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        club_self = Club(self.server_id, self.char_id)
        club_target = Club(self.server_id, int(club_id))

        key = str(arrow.utcnow().timestamp) + ',' + str(self.char_id) + ',' + club_id
        msg = ClubMatch(club_self, club_target).start()
        msg.key = key
        return msg

    def rise_in_rank_match(self, level):
        updater = {}
        docs = MongoLeague.db(self.server_id).find({'level': level+1}).sort('score', 1).limit(MAX_MATCH_CLUB)
        for doc in docs:
            club = MongoLeague.MATCH_CLUB_DOCUMENT
            club['flag'] = doc['flag']
            club['name'] = doc['name']
            club['win_rate'] = doc['win_rate']
            club['score'] = doc['score']

            updater[str(doc['_id'])] = club

        if updater:
            MongoLeague.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {'match_club': updater}}
            )

            self.notify_match_club()

    def notify_user_info(self):
        doc = MongoLeague.db(self.server_id).find_one({'_id': self.char_id}, {'level': 1, 'win_rate': 1})

        notify = LeagueUserNotify()
        notify.level = doc['level']
        notify.win_rate = doc['win_rate']
        MessagePipe(self.char_id).put(msg=notify)

    def notify_match_club(self, act=ACT_INIT, club_ids=None):
        # notify user match club info
        if not club_ids:
            projection = {'match_club': 1}
        else:
            act = ACT_UPDATE
            projection = {'match_club.{0}'.format(club_id): 1 for club_id in club_ids}

        doc = MongoLeague.db(self.server_id).find_one({'_id': self.char_id}, projection)

        notify = LeagueCLubNotify()
        notify.act = act

        for club in doc['match_clb']:
            notify_club = notify.match.add()
            notify_club.flag = club['flag']
            notify_club.name = club['name']
            notify_club.score = club['score']
            notify_club.win_rate = club['win_rate']

        MessagePipe(self.char_id).put(msg=notify)

