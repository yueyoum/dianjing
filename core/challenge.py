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
from utils.api import Timerd

from config import ConfigChallengeType, ConfigChallengeMatch, ConfigStaff, ConfigErrorMessage

from protomsg.challenge_pb2 import ChallengeNotify, ChallengeEnergyNotify
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE


CHALLENGE_MATCH_COST = 3                # 挑战赛花费体力值

NORMAL_ENERGIZE_TIME = 5 * 60           # 普通充能耗时
VIP_ENERGIZE_TIME = 4 * 60              # vip 充能耗时

ENERGIZE_NUM = 1                        # 定时能量回复


TIMERD_CALLBACK_PATH = '/api/timerd/challenge/energy/'


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
    # __slots__ = ['server_id', 'char_id']

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

    def refresh_challenge_times(self, area_id, challenge_id):
        MongoChallenge.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {'areas.{0}.challenges.{1}.times'.format(area_id, challenge_id): 0}}
        )

        self.challenge_notify(area_id=area_id)

    def check_energize(self):
        """
        检测是否需要注册充能定时任务
        """
        doc = MongoCharacter.db(self.server_id).find_one({'_id': self.char_id}, {'energy': 1, 'club.vip': 1})

        # 如果正在充能， 直接返回
        if doc['energy']['key']:
            return

        # 充能耗时
        if doc['club']['vip'] > 1:
            # 是否需要充能
            if doc['energy']['power'] > VIP_MAX_ENERGY:
                return

            end_at = arrow.utcnow().timestamp + VIP_ENERGIZE_TIME
        else:
            # 是否需要充能
            if doc['energy']['power'] > NORMAL_MAX_ENERGY:
                return

            end_at = arrow.utcnow().timestamp + NORMAL_ENERGIZE_TIME

        data = {
                'sid': self.server_id,
                'cid': self.char_id,
            }

        Timerd.register(end_at, TIMERD_CALLBACK_PATH, data)

    def energize_callback(self):
        """
        定时充能回调
        """
        self.add_energy(ENERGIZE_NUM)
        self.check_energize()

    def add_energy(self, num, times=0):
        """
        增加能量
        """
        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {'energy.power': num, 'energy.times': times}}
        )

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
        # 解析key
        club_one, area_id, challenge_id = str(key).split(',')

        # 判断是否是用户自身比赛
        if club_one != str(self.char_id):
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        # 更新员工胜率
        StaffManger(self.server_id, self.char_id).update_winning_rate(result)

        # 扣除能量
        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {'energy.power': -CHALLENGE_MATCH_COST}}
        )

        # 检查重能
        self.check_energize()

        # 更新挑战次数
        updater = {'areas.{0}.challenges.{1}.times'.format(area_id, challenge_id): 1}
        MongoChallenge.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': updater}
        )

        # 通关处理
        if win_club == club_one:
            counter = 0
            for r in result:
                if r.staff_one_win:
                    counter += 1

            if counter == 5:            # 3星
                stars = 3
            elif counter == 4:          # 2星
                stars = 2
            else:                       # 1星
                stars = 1
            doc = MongoChallenge.db(self.server_id).find_one(
                {'_id': self.char_id}, {'areas.{0}'.format(area_id): 1}
            )

            setter = {}
            # 判断是否需要更新星级
            if stars > doc['areas'][area_id]['challenges'].get(challenge_id, {}).get('stars', 0):
                setter['areas.{0}.challenges.{1}.stars'.format(area_id, challenge_id)] = stars

            next_challenge_id = int(challenge_id) + 1
            next_area_id = int(area_id) + 1

            elite_open = True
            # 如果下一关存在
            if ConfigChallengeMatch.get(next_challenge_id):
                # 如果是下一大区的， 开启新大区
                if ConfigChallengeType.get(int(area_id)).condition_challenge_id < next_challenge_id:
                    setter['areas.{0}.challenges.{1}'.format(next_area_id, next_challenge_id)] = {'stars': 0,
                                                                                                  'times': 0}
                    setter['areas.{0}.packages'.format(next_area_id)] = {'1': True, '2': True, '3': True}

                    self.challenge_notify(area_id=next_area_id)
                # 如果是当前大区的
                else:
                    # 如果还没开启
                    if str(next_challenge_id) not in doc['areas'][str(area_id)]['challenges']:
                        setter['areas.{0}.challenges.{1}'.format(area_id, next_challenge_id)] = {'stars': 0,
                                                                                                 'times': 0}
                    elite_open = False

            # 是否开启精英赛
            if elite_open:
                from core.elite_match import EliteMatch
                EliteMatch(self.server_id, self.char_id).open_area(int(area_id))

            # 更新数据
            if setter:
                MongoChallenge.db(self.server_id).update_one(
                    {'_id': self.char_id},
                    {'$set': setter}
                )

            # 同步到客户端
            self.challenge_notify(area_id=area_id)

            # # 通关奖励
            drop = Drop.generate(ConfigChallengeMatch.get(int(challenge_id)).package)
            Resource(self.server_id, self.char_id).save_drop(drop)
            return drop.make_protomsg()

        # send signal
        challenge_match_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            challenge_id=int(challenge_id),
            win=(win_club == club_one),
        )

        return None

    def get_star_reward(self, area_id, index):
        """
        领取星级奖励
        """
        # 获取数据
        doc = MongoChallenge.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'areas.{0}.packages.{1}'.format(area_id, index+1): 1},
            {'areas.{0}.challenges'.format(area_id): 1},
        )

        # 判断是否有星级奖励（实际上是检测是否已开通大区）
        star_reward = doc['areas'].get(str(area_id), {}).get('packages', {})
        if not star_reward:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_REWARD_NOT_EXIST"))

        # 已领取
        if not star_reward[str(index+1)]:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_REWARD_HAVE_GET"))

        star_count = 0
        # 计算总星数
        for ch_id, ch_info in doc['areas'][str(area_id)]['challenges'].iteritems():
            star_count += ch_info['stars']

        conf = ConfigChallengeType.get(area_id)
        # 星数不足
        if conf.star_reward[index]['star'] > star_count:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_REWARD_STARS_NOT_ENOUGH"))

        # 发放奖励
        drop = Drop.generate(conf.star_reward[index]['reward'])
        Resource(self.server_id, self.char_id).save_drop(drop)

        return drop.make_protomsg()

    def buy_energy(self):
        """
        购买 体力
        """
        # 是否还有购买次数
        doc = MongoCharacter.db(self.server_id).find_one({'_id': self.char_id}, {'energy': 1})
        if doc['energy']['times'] > 4:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_NO_BUY_ENERGY_TIMES"))

        # 扣除花费， 添加体力和购买次数
        with Resource(self.server_id, self.char_id).check(diamond=50, message="Buy energy power cost 50"):
            self.add_energy(20, 1)

    def energy_notify(self):
        doc = MongoCharacter.db(self.server_id).find_one({'_id': self.char_id}, {'energy.power': 1, 'club.vip': 1})

        notify = ChallengeEnergyNotify()
        notify.cur_energy = doc['energy']['power']
        if doc['club']['vip'] > 0:
            notify.max_energy = VIP_MAX_ENERGY
        else:
            notify.max_energy = NORMAL_MAX_ENERGY

        notify.refresh_time = 0

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

        MessagePipe(self.char_id).put(msg=notify)
