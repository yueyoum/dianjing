# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       game
Date Created:   2015-11-10 15:52
Description:

"""
import arrow
import random

from dianjing.exception import GameException

from core.character import Character
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


def get_league_refresh_time(server_id):
    return server_id


class LeagueNpcStaff(AbstractStaff):
    __slots__ = []

    def __init__(self, data):
        super(LeagueNpcStaff, self).__init__()

        self.id = data['id']
        config = ConfigStaff.get(self.id)

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

        self.policy = 1

        for k, v in data['staffs'].iteritems():
            self.match_staffs.append(v['id'])
            self.staffs[v['id']] = LeagueNpcStaff(v)

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
            self.normal_refresh()

        doc_self = MongoLeague.db(self.server_id).find_one({'_id': self.char_id})
        self.level = doc_self['level']
        self.score = doc_self['score']
        self.challenge_times = doc_self['challenge_times']
        self.total = doc_self['win_rate']['total']
        self.win = doc_self['win_rate']['win']
        self.in_rise = doc_self['in_rise']
        self.match_club = doc_self['match_club']
        self.daily_reward = doc_self['daily_reward']

    @classmethod
    def timer_refresh(cls, server_id):
        """
        刷新 -- 定时刷新
        """
        char_ids = Character.get_recent_login_char_ids(server_id)
        for char_id in char_ids:
            LeagueManger(server_id, char_id).normal_refresh()

    @classmethod
    def refresh_challenge_times(cls, server_id):
        """
        刷新 -- 挑战次数
        """
        char_ids = Character.get_recent_login_char_ids(server_id)
        for char_id in char_ids:
            MongoLeague.db(server_id).update_one(
                {'_id': char_id},
                {'$set': {'challenge_times': MAX_CHALLENGE_TIMES}}
            )

    def diamond_refresh(self):
        """
        钻石刷新 -- 匹配俱乐部
        """
        need_diamond = REFRESH_DIAMOND_COST
        message = u"Refresh {0} League Match CLub".format(self.char_id)
        # 扣除钻石
        with Resource(self.server_id, self.char_id).check(diamond=-need_diamond, message=message):
            self.normal_refresh(True)

    def normal_refresh(self, diamond_refresh=False,):
        """
        普通刷新 -- 匹配俱乐部
        """
        # 检查是否在晋级赛状态
        doc_self = MongoLeague.db(self.server_id).find_one({'_id': self.char_id})
        if doc_self['in_rise']:
            raise GameException(ConfigErrorMessage.get_error_id("IN_RISE_IN_RANK"))
        # 刷新
        self.refresh(diamond_refresh, doc_self['level'], doc_self['score'])
        # 同步到客户端
        self.notify_match_club()

    def rise_in_rank_match_refresh(self, level):
        """
        晋级刷新 -- 匹配俱乐部
        """
        self.refresh(level=level, score=1)
        MongoLeague.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'in_rise': True}}
        )
        self.notify_match_club()

    def refresh(self, diamond_refresh=False, level=1, score=1):
        """
        刷新 -- 匹配俱乐部
        """
        # 查找club
        updater = {}
        # 根据玩家等级， 积分 分配对手
        docs = MongoLeague.db(self.server_id).find(
            {'level': level, 'score': {'$gte': score}}
        ).sort('score', 1).limit(MAX_MATCH_CLUB * 10)
        doc_list = []
        for doc in docs:
            if not doc['in_rise']:
                doc_list.append(doc)

        if doc_list.__len__() >= MAX_MATCH_CLUB:
            need_num = MAX_MATCH_CLUB
        else:
            need_num = doc_list.__len__()

        need_npc = MAX_MATCH_CLUB
        # 先从玩家club中抽取
        if doc_list:
            clubs = random.sample(doc_list, need_num)
            for doc in clubs:
                if doc['_id'] != self.char_id:
                    club = {}
                    need_npc -= 1
                    club['flag'] = 0
                    club['name'] = ""
                    club['manager_name'] = ""
                    club['npc_club'] = False
                    club['staffs'] = {}
                    club['win_rate'] = {'total': 0, 'win': 0}
                    club['score'] = 0
                    club['status'] = ABLE

                    updater[str(doc['_id'])] = club

        # 玩家club不足， npc填补
        if need_npc > 0:
            npc_clubs = ConfigNPC.random_npcs(need_npc, league_level=level)
            for npc_club in npc_clubs:
                club = {}
                staffs = {}

                club['flag'] = npc_club['club_flag']
                club['name'] = npc_club['club_name']
                club['manager_name'] = npc_club['manager_name']
                club['npc_club'] = True
                club['win_rate'] = {'total': random.randint(30, 75), 'win': random.randint(20, 30)}
                club['score'] = random.randint(score, 999)
                club['status'] = ABLE

                for s in npc_club['staffs']:
                    staff = s
                    staff['race_win_rate'] = {
                        '1': {'total': random.randint(30, 75), 'win': random.randint(20, 30)},
                        '2': {'total': random.randint(30, 75), 'win': random.randint(20, 30)},
                        '3': {'total': random.randint(30, 75), 'win': random.randint(20, 30)}
                    }
                    staffs[str(s['id'])] = staff

                club['staffs'] = staffs
                updater[make_string_id()] = club

        # 钻石刷新，不刷新刷新时间
        if not diamond_refresh:
            refresh_time = arrow.utcnow().timestamp + REFRESH_TIME
        else:
            refresh_time = get_league_refresh_time(self.server_id)

        # 写入数据库
        MongoLeague.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'refresh_time': refresh_time,
                'match_club': updater}}
        )

    def report(self, key, win_club, result):
        """
        战斗结果汇报
            客户端返回战斗结果， 服务端处理结果数据
        """
        timestamp, club_one_id, club_two_id, npc_club = str(key).split(',')
        # 如果不是自己的战斗, 直接返回
        if club_one_id != str(self.char_id):
            return

        # 员工胜率处理胜率处理
        StaffManger(self.server_id, self.char_id).update_winning_rate(result)

        # 获取玩家是否为晋级赛
        doc = MongoLeague.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'in_rise': 1}
        )

        # 是否时晋级赛
        if not doc['in_rise']:
            # 积分赛处理
            self.normal_result(win_club == str(self.char_id), True, club_two_id)
        else:
            # 晋级赛处理
            self.rise_rank_result(win_club == str(self.char_id), club_two_id)

        # 对手处理
        if npc_club == 'False':
            # 对手为玩家处理
            # 员工胜率处理
            StaffManger(self.server_id, int(club_two_id)).update_winning_rate(result, False)
            # 被挑战者处理
            LeagueManger(self.server_id, int(club_two_id)).normal_result(not win_club == str(self.char_id))
        else:
            # 对手为npc处理
            doc = MongoLeague.db(self.server_id).find_one(
                {'_id': self.char_id},
                {'match_club.{0}'.format(club_two_id): 1}
            )

            # 有可能已被刷新掉
            if doc.get('match_club', {}).get(club_two_id, {}):
                npc_updater = {}

                # npc 胜率
                if not win_club == str(self.char_id):
                    npc_updater['match_club.{0}.win_rate.win'.format(club_two_id)] = 1
                npc_updater['match_club.{0}.win_rate.total'.format(club_two_id)] = 1

                # npc staff 胜率
                for r in result:
                    npc_updater['match_club.{0}.staffs.{1}.race_win_rate.total'.format(club_two_id, r.staff_two)] = 1
                    if not r.staff_one_win:
                        npc_updater['match_club.{0}.staffs.{1}.race_win_rate.win'.format(club_two_id, r.staff_two)] = 1

                # 更新到数据库
                MongoLeague.db(self.server_id).update_one(
                    {'_id': self.char_id},
                    {'$inc': npc_updater}
                )

    def normal_result(self, win=False, challenger=False, club_two_id=""):
        """
        积分赛结果处理
        """
        score = self.score
        # 获得积分、挑战状态、胜率
        if win:
            if challenger:
                score += CHALLENGE_WIN_GET_SCORE
            else:
                score += DEFENCE_WIN_GET_SCORE
            win_time_add = 1
            status = SUCCESS
        else:
            if challenger:
                score += DEFENCE_LOST_GET_SCORE
            else:
                score += CHALLENGE_LOST_GET_SCORE
            win_time_add = 0
            status = ABLE

        # 扣分
        if score < 0:
            # 等级高于一级, 掉级
            if self.level > 1:
                score += ConfigLeague.get(self.level - 1).up_need_score
            # 等级为一,无法掉级,分数置为一
            else:
                score = 1

        # 加分， 判断是否进入晋级赛
        up_need_score = ConfigLeague.get(self.level).up_need_score
        if score >= up_need_score:
            score = up_need_score
            self.rise_in_rank_match_refresh(self.level + 1)

        # 设置被挑战者 挑战状态， 自身积分
        setter = {'score': score}
        if club_two_id:
            doc = MongoLeague.db(self.server_id).find_one(
                {'_id': self.char_id},
                {'match_club.{0}'.format(club_two_id): 1}
            )
            # 有可能已被刷新掉
            if doc.get('match_club', {}).get(club_two_id, {}):
                setter['match_club.{0}.status'.format(club_two_id)] = status

        # 更新数据库
        MongoLeague.db(self.server_id).update_one(
            {'_id': self.char_id},
            {
                '$set': setter,
                '$inc': {'challenge_times': -1,
                         'win_rate.total': 1,
                         'win_rate.win': win_time_add,
                         }
            }
        )
        # 同步用户信息
        self.notify_user_info()

    def rise_rank_result(self, win=False, club_id=""):
        """
        晋级赛结果处理
        """
        if win:
            result = SUCCESS
            win_time_add = 1
        else:
            result = FAIL
            win_time_add = 0

        MongoLeague.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'match_club.{0}.status'.format(club_id): result},
             '$inc': {'win_rate.total': 1,
                      'win_rate.win': win_time_add}
             }
        )

        doc = MongoLeague.db(self.server_id).find_one({'_id': self.char_id}, {'match_club': 1})
        fail_times = 0
        success_times = 0
        for club_id, club_info in doc['match_club'].iteritems():
            if club_info['status'] == SUCCESS:
                success_times += 1
            elif club_info['status'] == FAIL:
                fail_times += 1

        # 晋级成功
        if success_times >= 3:
            MongoLeague.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {'level': self.level + 1, 'score': 1, 'in_rise': False}}
            )
            self.normal_refresh()

        # 晋级失败
        elif fail_times > 3:
            MongoLeague.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$inc': {'score': -RISE_IN_RANK_FAIL_PUNISH},
                 '$set': {'in_rise': False}
                 }
            )
            self.normal_refresh()

    def get_daily_reward(self):
        # 获取日常奖励
        doc = MongoLeague.db(self.server_id).find_one({'_id': self.char_id}, {'match_club': 0})

        if doc['daily_reward'] == str(arrow.now().date()):
            # 已领取
            raise GameException(ConfigErrorMessage.get_error_id("DAILY_REWARD_HAVE_GOT"))
        # 获取奖励配置
        conf = ConfigLeague.get(doc['level'])
        drop = Drop.generate(conf.daily_reward)
        # 发放奖励
        Resource(self.server_id, self.char_id).save_drop(drop, message="Add League Daily Reward")
        MongoLeague.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {"daily_reward": str(arrow.now().date())}}
        )
        # 同步玩家信息
        self.notify_user_info()
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

        # 检查是否有该挑战, 有可能刷新掉了
        if club_id not in doc['match_club']:
            raise GameException(ConfigErrorMessage.get_error_id("NO_THIS_CHALLENGE"))

        # 检查玩家是否有挑战次数
        if doc['challenge_times'] < 1 and not doc['in_rise']:
            raise GameException(ConfigErrorMessage.get_error_id("NO_CHALLENGE_TIMES"))

        # 非可挑战状态，不能再次挑战
        if doc['match_club'][club_id]['status'] != ABLE:
            raise GameException(ConfigErrorMessage.get_error_id("CLUB_HAVE_MATCH_CHALLENGE"))

        # 实例化俱乐部
        club_self = Club(self.server_id, self.char_id)
        club_tmp = doc['match_club'][club_id]
        club_two = LeagueClub(self.server_id, club_id, club_tmp)

        # 挑战信息
        key = str(arrow.utcnow().timestamp) + ',' + str(self.char_id) + ',' + club_id + ',' + str(club_tmp['npc_club'])
        msg = ClubMatch(club_self, club_two).start()
        msg.key = key

        return msg

    def get_club_detail(self, club_id):
        doc = MongoLeague.db(self.server_id).find_one({'_id': self.char_id}, {'match_club.{0}.staffs'.format(club_id): 1})
        if doc['match_club'].get(club_id, {}).get('npc_club', False):
            return doc['match_club'].get(club_id, {}).get('staffs', {})
        else:
            staff_ids = Club(self.server_id, int(club_id)).match_staffs
            return StaffManger(self.server_id, int(club_id)).get_winning_rate(staff_ids)

    def send_notify(self):
        self.notify_user_info()
        self.notify_match_club()

    def notify_user_info(self):
        doc = MongoLeague.db(self.server_id).find_one({'_id': self.char_id}, {'match_club': 0})

        notify = LeagueUserNotify()
        notify.score = doc['score']
        notify.level = doc['level']
        notify.challenge_times = doc['challenge_times']
        notify.has_reward = not doc['daily_reward'] == str(arrow.utcnow().date())

        if doc['win_rate']['total']:
            notify.win_rate = doc['win_rate']['win'] * 100 / doc['win_rate']['total']
        else:
            notify.win_rate = 0

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
                notify_club.win_rate = v['win_rate']['win'] * 100 / v['win_rate']['total']
            else:
                club_doc = MongoCharacter.db(self.server_id).find_one({'_id': int(k)}, {'club': 1})
                notify_club.flag = club_doc['club']['flag']
                notify_club.name = club_doc['club']['name']

                league_doc = MongoLeague.db(self.server_id).find_one({'_id': int(k)})
                notify_club.score = league_doc['score']
                if league_doc['win_rate']['total']:
                    notify_club.win_rate = league_doc['win_rate']['win'] * 100 / league_doc['win_rate']['total']
                else:
                    notify_club.win_rate = 0

            notify_club.club_id = k
            notify_club.status = v['status']

        MessagePipe(self.char_id).put(msg=notify)
