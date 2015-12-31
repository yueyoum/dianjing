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
from core.mongo import MongoLeague, MongoCharacter
from core.package import Drop
from core.match import ClubMatch
from core.club import Club
from core.staff import StaffManger
from core.abstract import AbstractStaff, AbstractClub

from config.league import ConfigLeague
from config.errormsg import ConfigErrorMessage
from config.npc import ConfigNPC
from config.staff import ConfigStaff

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.league_pb2 import (
    LeagueUserNotify,
    LeagueClubNotify,
    ABLE,
    FAIL,
    SUCCESS,
    UNABLE,
)
from protomsg.staff_pb2 import Staff as MessageStaff

from utils.message import MessagePipe
from utils.functional import make_string_id


MAX_CHALLENGE_TIMES = 7
MAX_MATCH_CLUB = 6

REFRESH_DIAMOND_COST = 200
REFRESH_TYPE_NORMAL = 1
REFRESH_TYPE_DIAMOND = 2
REFRESH_TIME = 6 * 60 * 60

RISE_IN_RANK_FAIL_PUNISH = 300

CHALLENGE_WIN_GET_SCORE = 3
CHALLENGE_LOST_GET_SCORE = 0
DEFENCE_WIN_GET_SCORE = 0
DEFENCE_LOST_GET_SCORE = -3


class LeagueNpcStaff(AbstractStaff):
    __slots__ = []

    def __init__(self, data):
        super(LeagueNpcStaff, self).__init__()

        self.id = data['id']
        config = ConfigStaff.get(self.id)

        # TODO
        self.level = 1
        self.race = config.race
        skill_level = data.get('skill_level', 1)
        self.skills = {i: skill_level for i in config.skill_ids}

        self.luoji = config.luoji
        self.minjie = config.minjie
        self.lilun = config.lilun
        self.wuxing = config.wuxing
        self.meili = config.meili

        self.calculate_secondary_property()

    def make_protomsg(self):
        msg = MessageStaff()

        msg.id = self.id
        msg.level = self.level
        msg.cur_exp = 0
        msg.max_exp = 1000
        msg.status = 3

        msg.luoji = 1
        msg.minjie = 1
        msg.lilun = 1
        msg.wuxing = 1
        msg.meili = 1

        msg.caozuo = int(self.caozuo)
        msg.jingying = int(self.jingying)
        msg.baobing = int(self.baobing)
        msg.zhanshu = int(self.zhanshu)

        msg.biaoyan = 1
        msg.yingxiao = 1

        msg.zhimingdu = 1

        return msg


class LeagueNpcClub(AbstractClub):
    def __init__(self, club_id, data):
        super(LeagueNpcClub, self).__init__()
        self.id = club_id
        self.name = data['name']
        self.manager_name = data['manager_name']
        self.flag = data['flag']
        # TODO
        self.policy = 1

        for s in data['staffs']:
            self.match_staffs.append(s['id'])
            self.staffs[s['id']] = LeagueNpcStaff(s)

        self.qianban_affect()

        self.score = data['score']


class LeagueClub(object):
    def __new__(cls, server_id, club_id, data):
        if data['npc_club']:
            return LeagueNpcClub(club_id, data)
        else:
            return Club(server_id, int(club_id))


class LeagueManger(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoLeague.exist(self.server_id, self.char_id):
            doc = MongoLeague.DOCUMENT
            doc['_id'] = self.char_id
            doc['challenge_times'] = MAX_CHALLENGE_TIMES
            MongoLeague.db(self.server_id).insert_one(doc)
            # first create, add match club
            self.refresh()

        doc_self = MongoLeague.db(self.server_id).find_one({'_id': self.char_id})
        self.level = doc_self['level']
        self.score = doc_self['score']
        self.challenge_times = doc_self['challenge_times']
        self.win_rate = doc_self['win_rate']
        self.in_rise = doc_self['in_rise']
        self.match_club = doc_self['match_club']
        self.daily_reward = doc_self['daily_reward']

    def timer_refresh(self):
        pass

    def diamond_refresh(self):
        need_diamond = REFRESH_DIAMOND_COST
        message = u"Refresh {0} League Match CLub".format(self.char_id)
        with Resource(self.server_id, self.char_id).check(need_diamond=-need_diamond, message=message):
            self.refresh()

    def refresh(self):
        """
        refresh the match_club
        """
        # 检查是否在晋级赛状态
        doc_self = MongoLeague.db(self.server_id).find_one({'_id': self.char_id})
        if doc_self['in_rise']:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))
        # 查找club
        updater = {}
        docs = MongoLeague.db(self.server_id).find(
            {'level': doc_self['level'], 'score': {'$gte': doc_self['score']}}
        ).sort('score', 1).limit(MAX_MATCH_CLUB)

        need_npc = MAX_MATCH_CLUB
        if docs:
            for doc in docs:
                if doc['_id'] != self.char_id and need_npc > 0:
                    club = {}
                    need_npc -= 1
                    club['flag'] = 0
                    club['name'] = ""
                    club['manager_name'] = ""
                    club['npc_club'] = False
                    club['staffs'] = []
                    club['win_rate'] = 0
                    club['score'] = 0
                    club['status'] = ABLE

                    updater[str(doc['_id'])] = club

        if need_npc > 0:
            npc_clubs = ConfigNPC.random_npcs(need_npc, league_level=1)
            for npc_club in npc_clubs:
                club = {}
                club['flag'] = npc_club['club_flag']
                club['name'] = npc_club['club_name']
                club['manager_name'] = npc_club['manager_name']
                club['npc_club'] = True
                club['staffs'] = npc_club['staffs']
                club['win_rate'] = 0
                club['score'] = 0
                club['status'] = ABLE

                updater[make_string_id()] = club
        print '**' * 20
        for up in updater:
            print up
        print '**' * 20

        refresh_time = arrow.utcnow().timestamp + REFRESH_TIME
        MongoLeague.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'refresh_time': refresh_time,
                'match_club': updater
            }}
        )

        self.notify_match_club()

    def report(self, key, win_club, result):
        """
        战斗结果汇报
            客户端返回战斗结果， 服务端处理结果数据
        """
        timestamp, club_one, club_two, npc_club = str(key).split(',')
        # 如果不是自己的战斗, 直接返回
        if club_one != str(self.char_id):
            return
        # 员工胜率处理胜率处理
        StaffManger(self.server_id, self.char_id).update_winning_rate(result)
        if npc_club == 'False':
            StaffManger(self.server_id, club_two).update_winning_rate(result, False)
        # 写入数据库
        MongoLeague.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {'challenge_times': -1}}
        )

        doc = MongoLeague.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'in_rise': 1, 'match_club.{0}'.format(club_two): 1})

        if not doc['in_rise']:
            self.normal_result(win_club == str(self.char_id), True)
            if not doc['match_club'][club_two]['npc_club']:
                LeagueManger(self.server_id, int(club_two)).normal_result(not win_club == str(self.char_id), False)
        else:
            self.rise_rank_result(win_club == str(self.char_id))

    def normal_result(self, win=False, challenger=False):
        """
        普通汇报结果处理
        """
        score = self.score
        # 得分计算
        if win:
            if challenger:
                score += CHALLENGE_WIN_GET_SCORE
            else:
                score += DEFENCE_WIN_GET_SCORE
        else:
            if challenger:
                score += DEFENCE_LOST_GET_SCORE
            else:
                score += CHALLENGE_LOST_GET_SCORE
        # 扣分
        if score < 0:
            # 等级高于一级, 掉级
            if self.level > 1:
                score += ConfigLeague.get(self.level -1).up_need_score
            # 等级为一,无法掉级,分数置为一
            else:
                score = 0
        # 更新数据库
        up_need_score = ConfigLeague.get(self.level).up_need_score
        if score >= up_need_score:
            score = up_need_score
            self.rise_in_rank_match(self.level + 1)

        MongoLeague.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'score': score}}
        )

        self.notify_user_info()

    def rise_rank_result(self, win=False):
        """
        联赛晋级结果汇报处理
        """
        if win:
            pass
        else:
            pass

    def get_daily_reward(self):
        # get current daily reward
        doc = MongoLeague.db(self.server_id).find_one({'_id': self.char_id}, {'match_club': 0})

        if doc['daily_reward'] == str(arrow.now().date()):
            # already got
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        conf = ConfigLeague.get(doc['level'])
        drop = Drop.generate(conf.daily_reward)

        Resource(self.server_id, self.char_id).save_drop(drop, message="Add League Daily Reward")
        MongoLeague.db(self.server_id).update_one(
            {'_id': self.char_id},
                {'$set': {"daily_reward": str(arrow.now().date())}}
        )

        return drop.make_protomsg()

    def challenge(self, club_id):
        """
        挑战俱乐部
        """
        # 获取被挑战者信息
        doc = MongoLeague.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'match_club.{0}'.format(club_id): 1, 'challenge_times': 1}
        )
        # 检查是否有该挑战
        if club_id not in doc['match_club']:
            raise GameException(ConfigErrorMessage.get_error_id("NO_THIS_CHALLENGE"))
        # 检查玩家是否有挑战次数
        if doc['challenge_times'] < 1:
            raise GameException(ConfigErrorMessage.get_error_id("NO_CHALLENGE_TIMES"))
        # 实例化俱乐部
        club_self = Club(self.server_id, self.char_id)
        club_target = doc['match_club'][club_id]
        club_two = LeagueClub(self.server_id, club_id, club_target)
        # 挑战信息
        key = str(arrow.utcnow().timestamp) + ',' + str(self.char_id) + ',' + club_id + ',' + str(club_target['npc_club'])
        msg = ClubMatch(club_self, club_two).start()
        msg.key = key
        print msg
        return msg

    def rise_in_rank_match(self, level):
        updater = {}
        docs = MongoLeague.db(self.server_id).find({'level': level+1}).sort('score', 1).limit(MAX_MATCH_CLUB)
        for doc in docs:
            if doc:
                club = MongoLeague.MATCH_CLUB_DOCUMENT
                club['flag'] = doc['flag']
                club['name'] = doc['name']
                club['win_rate'] = doc['win_rate']
                club['score'] = doc['score']
                club['status'] = ABLE

                updater[make_string_id()] = club

        if updater:
            MongoLeague.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {'match_club': updater}}
            )

            self.notify_match_club()

    def get_club_detail(self, club_id):
        # todo: user staff detail
        staffs = []
        print 'get_club_detail', club_id
        doc = MongoLeague.db(self.server_id).find_one({'_id': self.char_id}, {'match_club.{0}'.format(club_id): 1})
        if doc['match_club'][club_id].get('npc_club', False):
            for staff in doc['match_club'][club_id]['staffs']:
                staffs.append(LeagueNpcStaff(staff).make_protomsg())
        else:
            staff_ids = Club(self.server_id, int(club_id)).match_staffs
            for staff_id in staff_ids:
                staffs.append(StaffManger(self.server_id, self.char_id).get_staff(staff_id).make_protomsg())
        return staffs

    def send_notify(self):
        self.notify_user_info()
        self.notify_match_club()

    def notify_user_info(self):
        doc = MongoLeague.db(self.server_id).find_one({'_id': self.char_id}, {'match_club': 0})

        notify = LeagueUserNotify()
        notify.score = doc['score']
        notify.level = doc['level']
        notify.win_rate = doc['win_rate']
        notify.challenge_times = doc['challenge_times']
        notify.has_reward = not doc['daily_reward'] == str(arrow.utcnow().date())
        MessagePipe(self.char_id).put(msg=notify)

    def notify_match_club(self, act=ACT_INIT, club_ids=None):
        # notify user match club info
        if not club_ids:
            projection = {'match_club': 1, 'refresh_time': 1}
        else:
            act = ACT_UPDATE
            projection = {'match_club.{0}'.format(club_id): 1 for club_id in club_ids}
            projection = dict({'1': 'test'}, **projection)

        doc = MongoLeague.db(self.server_id).find_one({'_id': self.char_id}, projection)

        notify = LeagueClubNotify()
        notify.act = act
        notify.end_time = doc['refresh_time']

        for k, v in doc['match_club'].iteritems():
            notify_club = notify.clubs.add()

            if v['npc_club']:
                notify_club.flag = v['flag']
                notify_club.name = v['name']
                notify_club.score = v['score']
                notify_club.win_rate = v['win_rate']
            else:
                club_doc = MongoCharacter.db(self.server_id).find_one({'_id': int(k)}, {'club': 1})
                notify_club.flag = club_doc['club']['flag']
                notify_club.name = club_doc['club']['name']

                league_doc = MongoLeague.db(self.server_id).find_one({'_id': int(k)})
                notify_club.score = league_doc['score']
                notify_club.win_rate = league_doc['win_rate']

            notify_club.club_id = k
            notify_club.status = v['status']

        MessagePipe(self.char_id).put(msg=notify)

