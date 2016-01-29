# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2015-07-15 11:41
Description:

"""

import arrow

from dianjing.exception import GameException

from core.abstract import AbstractClub, AbstractStaff
from core.mongo import MongoChallenge, MongoCharacter
from core.club import Club
from core.match import ClubMatch
from core.staff import StaffManger
from core.character import Character, NORMAL_MAX_ENERGY, VIP_MAX_ENERGY

from core.package import Drop
from core.resource import Resource

from core.signals import challenge_match_signal

from utils.message import MessagePipe

from config import ConfigChallengeType, ConfigChallengeMatch, ConfigStaff, ConfigErrorMessage

from protomsg.challenge_pb2 import ChallengeNotify, ChallengeEnergyNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE


CHALLENGE_MATCH_COST = -6                   # 挑战赛花费体力值

NORMAL_ENERGIZE_NUM = 6                            # 定时能量回复

BUY_ENERGY_DIAMOND_COST = 50
BUY_ENERGY_ENERGIZE = 20
BUY_ENERGY_TIMES_ADD = 1
MAX_DAY_BUY_ENERGY_TIMES = 4

MATCH_LOSE_ZERO_ROUND = 5
MATCH_LOSE_ONE_ROUND = 4

LOSE_ZERO_ROUND_GET_STAR = 3
LOSE_ONE_ROUND_GET_STAR = 2
LOSE_TWO_ROUND_GET_STAR = 1


class ChallengeNPCStaff(AbstractStaff):
    __slots__ = []

    def __init__(self, _id, level, strength):
        super(ChallengeNPCStaff, self).__init__()

        self.id = _id
        self.level = level

        config = ConfigStaff.get(_id)
        self.race = config.race
        self.skills = {i: 1 for i in config.skill_ids}

        self.luoji = config.luoji * strength
        self.minjie = config.minjie * strength
        self.lilun = config.lilun * strength
        self.wuxing = config.wuxing * strength
        self.meili = config.meili * strength

        self.calculate_secondary_property()


class ChallengeNPCClub(AbstractClub):
    __slots__ = []

    def __init__(self, challenge_match_id):
        super(ChallengeNPCClub, self).__init__()

        config = ConfigChallengeMatch.get(challenge_match_id)

        self.id = challenge_match_id

        self.match_staffs = config.staffs
        self.policy = config.policy
        self.name = config.club_name
        self.flag = config.club_flag

        for i in self.match_staffs:
            self.staffs[i] = ChallengeNPCStaff(i, config.level, config.strength)

        self.qianban_affect()


class Challenge(object):
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoChallenge.exist(self.server_id, self.char_id):
            doc = MongoChallenge.document()
            # XXX 编辑器里面定死，不能胡乱填写
            # 1号大区，第一关默认开启
            doc['_id'] = self.char_id
            MongoChallenge.db(self.server_id).insert_one(doc)

    @classmethod
    def cronjob_refresh_times(cls, server_id):
        for char_id in Character.get_recent_login_char_ids(server_id):
            doc = MongoChallenge.db(server_id).find_one({'_id': char_id})

            updater = {}
            for area_id, area_info in doc['areas'].iteritems():
                for ch_id, ch_info in area_info['challenges']:
                    updater['areas.{0}.challenges.{1}.times'.format(area_id, ch_id)] = 0

            MongoChallenge.db(server_id).update_one(
                {'_id': char_id},
                {'$set': updater}
            )

            # 同时重置玩家钻石充能次数
            MongoCharacter.db(server_id).update_one(
                {'_id': char_id},
                {'$set': {'energy.times': 0}}
            )

    @classmethod
    def cronjob_energize(cls, server_id):
        for char_id in Character.get_recent_login_char_ids(server_id):

            doc = MongoCharacter.db(server_id).find_one({"_id": int(char_id)})
            if doc.get('club', {}).get("vip", 0):
                max_energy = VIP_MAX_ENERGY
            else:
                max_energy = NORMAL_MAX_ENERGY

            if doc.get('energy', {}).get("power", 0) + NORMAL_ENERGIZE_NUM <= max_energy:
                energize_num = NORMAL_ENERGIZE_NUM
            else:
                energize_num = max_energy - doc.get('energy', {}).get("power", 0)

            Challenge(server_id, int(char_id)).change_energy(energize_num)

    def current_challenge_id(self):
        doc = MongoChallenge.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'areas': 1}
        )

        tmp_area_id = max([int(area_id) for area_id in doc['areas'].keys()])

        tmp_ch_id = 0
        for ch_id in doc['areas'].get(str(tmp_area_id), {}).get("challenges", {}).keys():
            if tmp_ch_id < int(ch_id):
                if doc['areas'][str(tmp_area_id)]['challenges'][str(ch_id)]['stars'] > 0:
                    tmp_ch_id = int(ch_id)

        return tmp_ch_id

    def change_energy(self, num, times=0):
        """
        改变能量
        """
        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {'energy.power': num, 'energy.times': times}}
        )
        # 同步能量数据
        self.energy_notify()
        # self.check_energize()

    def start(self, area_id, challenge_id):
        """
        开始挑战关卡
            1 检测, 大区、关卡、是否开启，俱乐部等级是否满足，该关卡是否仍有挑战次数、体力是否足够
            2 ClubMatch
            3 返回对战双方信息
        """
        # 判断大区是否存在
        if not ConfigChallengeType.get(area_id):
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_AREA_NOT_EXIST"))

        # 俱乐部等级检查
        club_one = Club(self.server_id, self.char_id)
        config = ConfigChallengeMatch.get(challenge_id)
        if club_one.current_level() < config.need_club_level:
            raise GameException(ConfigErrorMessage.get_error_id("CLUB_LEVEL_NOT_ENOUGH"))

        # 获取玩家数据
        doc = MongoChallenge.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'areas.{0}.challenges.{1}'.format(area_id, challenge_id): 1}
        )

        # 判断大区是否已开启
        if not doc['areas'].get(str(area_id), {}):
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_AREA_NOT_OPEN"))

        # 判断是否已开方关卡
        challenge = doc['areas'][str(area_id)]['challenges'].get(str(challenge_id), {})
        if not challenge:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_NOT_OPEN"))

        # 体力检查
        doc_char = MongoCharacter.db(self.server_id).find_one({'_id': self.char_id}, {'energy': 1})
        if doc_char['energy']['power'] < CHALLENGE_MATCH_COST:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_NOT_ENOUGH_ENERGY"))

        # match
        club_two = ChallengeNPCClub(challenge_id)
        match = ClubMatch(club_one, club_two)

        msg = match.start()
        msg.key = str(self.char_id) + ',' + str(area_id) + ',' + str(challenge_id)
        return msg

    def report(self, key, win_club, result):
        club_one, area_id, challenge_id = str(key).split(',')

        if club_one != str(self.char_id):
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        StaffManger(self.server_id, self.char_id).update_winning_rate(result)

        self.deduct_challenge_energy_cost(CHALLENGE_MATCH_COST)

        updater = {'areas.{0}.challenges.{1}.times'.format(area_id, challenge_id): 1}
        MongoChallenge.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': updater},
        )

        challenge_match_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            challenge_id=int(challenge_id),
            win=(win_club == club_one),
        )

        if win_club != club_one:
            return

        doc = MongoChallenge.db(self.server_id).find_one(
            {'_id': self.char_id}, {'areas.{0}'.format(area_id): 1}
        )

        stars = self.calculate_stars(result)
        setter = {}
        doc_stars = doc['areas'][area_id]['challenges'].get(challenge_id, {}).get('stars', 0)

        if stars > doc_stars:
            setter['areas.{0}.challenges.{1}.stars'.format(area_id, challenge_id)] = stars

        next_challenge_id = int(challenge_id) + 1
        next_area_id = int(area_id) + 1

        elite_open = True
        if ConfigChallengeMatch.get(next_challenge_id):
            if ConfigChallengeType.get(int(area_id)).condition_challenge_id < next_challenge_id:
                setter['areas.{0}.challenges.{1}'.format(next_area_id, next_challenge_id)] = {'stars': 0, 'times': 0}
                self.open_new_area(next_area_id)
            else:
                if str(next_challenge_id) not in doc['areas'][str(area_id)]['challenges']:
                    setter['areas.{0}.challenges.{1}'.format(area_id, next_challenge_id)] = {'stars': 0, 'times': 0}
                elite_open = False

        if elite_open:
            from core.elite_match import EliteMatch
            EliteMatch(self.server_id, self.char_id).open_area(int(area_id))

        if setter:
            self.update_setter_data(setter)

        self.challenge_notify(area_id=area_id)

        drop = Drop.generate(ConfigChallengeMatch.get(int(challenge_id)).package)
        Resource(self.server_id, self.char_id).save_drop(drop)
        return drop.make_protomsg()

    def calculate_stars(self, result):
        win_rounds = 0
        for r in result:
            if r.staff_one_win:
                win_rounds += 1

        if win_rounds == MATCH_LOSE_ZERO_ROUND:
            return LOSE_ZERO_ROUND_GET_STAR
        elif win_rounds == MATCH_LOSE_ONE_ROUND:
            return LOSE_ONE_ROUND_GET_STAR
        else:
            return LOSE_TWO_ROUND_GET_STAR

    def open_new_area(self, area_id):
        config = ConfigChallengeType.get(area_id-1)
        setter = {
            'areas.{0}.challenges.{1}.stars'.format(area_id, config.condition_challenge_id+1): 0,
            'areas.{0}.challenges.{1}.times'.format(area_id, config.condition_challenge_id+1): 0,
            'areas.{0}.packages.1'.format(area_id): True,
            'areas.{0}.packages.2'.format(area_id): True,
            'areas.{0}.packages.3'.format(area_id): True,
        }

        self.update_setter_data(setter)
        self.challenge_notify(area_id=area_id)

    def update_setter_data(self, setter):
        MongoChallenge.db(self.server_id).update_one(
                    {'_id': self.char_id},
                    {'$set': setter}
        )

    def get_challenge_data(self):
        return MongoChallenge.db(self.server_id).find({'_id': self.char_id})

    def deduct_challenge_energy_cost(self, num):
        self.change_energy(num)

    def get_star_reward(self, area_id, index):
        """
        领取星级奖励
        """
        # 奖励不存在
        if index >= 3:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_REWARD_NOT_EXIST"))

        # 获取数据
        doc = MongoChallenge.db(self.server_id).find_one(
            {'_id': self.char_id},
            {
                'areas.{0}'.format(area_id): 1
             },
        )

        star_reward = doc['areas'].get(str(area_id), {}).get('packages', {})
        if not star_reward:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_REWARD_NOT_EXIST"))

        if not star_reward[str(index+1)]:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_REWARD_HAVE_GET"))

        star_count = 0
        for ch_id, ch_info in doc['areas'][str(area_id)]['challenges'].iteritems():
            star_count += ch_info['stars']

        conf = ConfigChallengeType.get(area_id)
        if conf.star_reward[index]['star'] > star_count:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_REWARD_STARS_NOT_ENOUGH"))

        drop = Drop.generate(conf.star_reward[index]['reward'])

        Resource(self.server_id, self.char_id).save_drop(drop)
        MongoChallenge.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'areas.{0}.packages.{1}'.format(area_id, index+1): False}}
        )

        self.challenge_notify(area_id=area_id)

        return drop.make_protomsg()

    def buy_energy(self):
        """
        购买 体力
        """
        doc = MongoCharacter.db(self.server_id).find_one({'_id': self.char_id}, {'energy': 1})
        if doc['energy']['times'] >= MAX_DAY_BUY_ENERGY_TIMES:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_NO_BUY_ENERGY_TIMES"))

        with Resource(self.server_id, self.char_id).check(
                diamond=BUY_ENERGY_DIAMOND_COST, message="Buy energy power cost {0}".format(BUY_ENERGY_DIAMOND_COST)):
            self.change_energy(BUY_ENERGY_ENERGIZE, BUY_ENERGY_TIMES_ADD)

    def energy_notify(self):
        doc = MongoCharacter.db(self.server_id).find_one({'_id': self.char_id}, {'energy.power': 1, 'club.vip': 1})

        notify = ChallengeEnergyNotify()
        notify.cur_energy = doc.get('energy', {}).get('power', 0)
        if doc['club']['vip'] > 0:
            notify.max_energy = VIP_MAX_ENERGY
        else:
            notify.max_energy = NORMAL_MAX_ENERGY

        time_now = arrow.utcnow()
        if time_now.time().minute <= 30:
            minute = 30
        else:
            minute = 60

        if notify.cur_energy < notify.max_energy:
            refresh_time = (minute - time_now.time().minute) * 60 + 60 - time_now.time().second
        else:
            refresh_time = 0

        notify.refresh_time = refresh_time

        MessagePipe(self.char_id).put(msg=notify)

    def challenge_notify(self, act=ACT_INIT, area_id=None):
        if area_id:
            act = ACT_UPDATE
            projection = {'areas.{0}'.format(area_id): 1}
        else:
            projection = {'areas': 1}

        doc = MongoChallenge.db(self.server_id).find_one({'_id': self.char_id}, projection)

        notify = ChallengeNotify()
        notify.act = act

        for k, v in doc['areas'].iteritems():

            notify_area = notify.area.add()
            notify_area.id = int(k)
            notify_area.package_one = v['packages']['1']
            notify_area.package_two = v['packages']['2']
            notify_area.package_three = v['packages']['3']

            for challenge_id, info in v['challenges'].iteritems():
                notify_challenge = notify_area.challenge.add()
                notify_challenge.id = int(challenge_id)
                notify_challenge.times = info['times']
                notify_challenge.stars = info['stars']

        print " * " * 25
        print notify
        MessagePipe(self.char_id).put(msg=notify)
