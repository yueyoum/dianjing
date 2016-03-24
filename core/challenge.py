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
from core.character import NORMAL_MAX_ENERGY, VIP_MAX_ENERGY

from core.resource import Resource

from core.signals import challenge_match_signal

from utils.message import MessagePipe

from config import ConfigChapter, ConfigChallengeMatch, ConfigStaffNew, ConfigErrorMessage

from protomsg.challenge_pb2 import (
    ChallengeNotify,
    ChallengeEnergyNotify,
    ChapterNotify,
    CHAPTER_REWARD_DONE,
    CHAPTER_REWARD_NOT,
    CHAPTER_REWARD_OK,
)

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE

CHALLENGE_MATCH_COST = -6  # 挑战赛花费体力值

NORMAL_ENERGIZE_NUM = 6  # 定时能量回复

BUY_ENERGY_DIAMOND_COST = 50
BUY_ENERGY_ENERGIZE = 20
BUY_ENERGY_TIMES_ADD = 1
MAX_DAY_BUY_ENERGY_TIMES = 4

MATCH_LOSE_ZERO_ROUND = 5
MATCH_LOSE_ONE_ROUND = 4

LOSE_ZERO_ROUND_GET_STAR = 3
LOSE_ONE_ROUND_GET_STAR = 2
LOSE_TWO_ROUND_GET_STAR = 1

STAR_REWARD_MAX_INDEX = 3


class ChallengeNPCStaff(AbstractStaff):
    __slots__ = []

    def __init__(self, _id, unit_id, position):
        super(ChallengeNPCStaff, self).__init__()

        self.id = _id
        self.level = 1

        # config = ConfigStaffNew.get(_id)
        # self.race =
        # self.skills = {i: 1 for i in config.skill_ids}
        #
        # self.luoji = config.luoji
        # self.minjie = config.minjie
        # self.lilun = config.lilun
        # self.wuxing = config.wuxing
        # self.meili = config.meili

        self.unit_id = unit_id
        self.position = position
        self.calculate_secondary_property()


class ChallengeNPCClub(AbstractClub):
    __slots__ = []

    def __init__(self, challenge_match_id):
        super(ChallengeNPCClub, self).__init__()

        config = ConfigChallengeMatch.get(challenge_match_id)

        self.id = challenge_match_id

        # TODO
        self.policy = 1
        self.name = config.name
        self.flag = 1

        for position, _id, unit_id in config.staffs:
            self.match_staffs.append(_id)
            self.staffs[_id] = ChallengeNPCStaff(_id, unit_id, position)

            # self.qianban_affect()


class Challenge(object):
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoChallenge.exist(self.server_id, self.char_id):
            doc = MongoChallenge.document()
            # XXX 编辑器里面定死，不能胡乱填写
            # 第一关默认开启 id 为 1
            doc['_id'] = self.char_id
            doc['challenge_star'] = {'1': 0}
            doc['challenge_times'] = {'1': 0}

            chapter_id = ConfigChallengeMatch.get(1).chapter
            doc['chapters'] = {
                str(chapter_id): {
                    'star': 0,
                    'rewards': []
                }
            }

            MongoChallenge.db(self.server_id).insert_one(doc)

    # @classmethod
    # def cronjob_refresh_times(cls, server_id):
    #     for char_id in Character.get_recent_login_char_ids(server_id):
    #         doc = MongoChallenge.db(server_id).find_one({'_id': char_id})
    #
    #         updater = {}
    #         for area_id, area_info in doc['areas'].iteritems():
    #             for ch_id, ch_info in area_info['challenges']:
    #                 updater['areas.{0}.challenges.{1}.times'.format(area_id, ch_id)] = 0
    #
    #         MongoChallenge.db(server_id).update_one(
    #             {'_id': char_id},
    #             {'$set': updater}
    #         )
    #
    #         # 同时重置玩家钻石充能次数
    #         MongoCharacter.db(server_id).update_one(
    #             {'_id': char_id},
    #             {'$set': {'energy.times': 0}}
    #         )
    #
    # @classmethod
    # def cronjob_energize(cls, server_id):
    #     from core.lock import Lock
    #     for char_id in Character.get_recent_login_char_ids(server_id):
    #
    #         doc = MongoCharacter.db(server_id).find_one({"_id": int(char_id)})
    #         if doc.get('club', {}).get("vip", 0):
    #             max_energy = VIP_MAX_ENERGY
    #         else:
    #             max_energy = NORMAL_MAX_ENERGY
    #
    #         if doc.get('energy', {}).get("power", 0) + NORMAL_ENERGIZE_NUM <= max_energy:
    #             energize_num = NORMAL_ENERGIZE_NUM
    #         else:
    #             energize_num = max_energy - doc.get('energy', {}).get("power", 0)
    #
    #         with Lock(server_id).lock(key="character_energize_{0}".format(char_id)):
    #             Challenge(server_id, int(char_id)).change_energy(energize_num)

    def current_challenge_id(self):
        # doc = MongoChallenge.db(self.server_id).find_one(
        #     {'_id': self.char_id},
        #     {'areas': 1}
        # )
        #
        # tmp_area_id = max([int(area_id) for area_id in doc['areas'].keys()])
        #
        # tmp_ch_id = 0
        # for ch_id in doc['areas'].get(str(tmp_area_id), {}).get("challenges", {}).keys():
        #     if tmp_ch_id < int(ch_id):
        #         if doc['areas'][str(tmp_area_id)]['challenges'][str(ch_id)]['stars'] > 0:
        #             tmp_ch_id = int(ch_id)
        #
        # return tmp_ch_id
        return 0

    # def change_energy(self, num, times=0):
    #     MongoCharacter.db(self.server_id).update_one(
    #         {'_id': self.char_id},
    #         {'$inc': {'energy.power': num, 'energy.times': times}}
    #     )
    #     self.energy_notify()
    #
    # def match_check(self, area_id, challenge_id):
    #     self.config_check(area_id)
    #
    #     doc = self.get_challenge_data({'areas.{0}.challenges.{1}'.format(area_id, challenge_id): 1})
    #     print doc
    #     if not doc['areas'].get(str(area_id), {}):
    #         raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_AREA_NOT_OPEN"))
    #
    #     challenge = doc['areas'][str(area_id)]['challenges'].get(str(challenge_id), {})
    #     if not challenge:
    #         raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_NOT_OPEN"))
    #
    #     self.energy_check()
    #
    # def energy_check(self):
    #     doc_char = MongoCharacter.db(self.server_id).find_one({'_id': self.char_id}, {'energy': 1})
    #     if doc_char['energy']['power'] < CHALLENGE_MATCH_COST:
    #         raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_NOT_ENOUGH_ENERGY"))
    #
    # def config_check(self, area_id):
    #     if not ConfigChallengeType.get(area_id):
    #         raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_AREA_NOT_EXIST"))


    def make_match_key(self, area_id, challenge_id):
        return "%s,%s,%s" % (self.char_id, area_id, challenge_id)

    def start(self, challenge_id):
        config = ConfigChallengeMatch.get(challenge_id)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        # TODO IO 优化
        doc = MongoChallenge.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'challenge_star': 1, 'challenge_times': 1}
        )

        if config.condition_challenge and str(config.condition_challenge) not in doc['challenge_star']:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_NOT_OPEN"))

        if doc['challenge_times'].get(str(challenge_id), 0) >= config.times_limit:
            # TODO error code
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        club_one = Club(self.server_id, self.char_id)
        club_two = ChallengeNPCClub(challenge_id)
        match = ClubMatch(club_one, club_two)
        msg = match.start()
        # TODO key
        msg.key = str(challenge_id)
        return msg

    def report(self, key, star):
        # club_one, area_id, challenge_id = str(key).split(',')
        #
        # if club_one != str(self.char_id):
        #     raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        challenge_id = int(key)
        config = ConfigChallengeMatch.get(challenge_id)

        # TODO IO 优化
        doc = MongoChallenge.db(self.server_id).find_one(
            {'_id': self.char_id}
        )

        MongoChallenge.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {
                'challenge_times.{0}'.format(challenge_id): 1
            }}
        )

        if star <= 0:
            self.send_challenge_notify(ids=[challenge_id])
            return

        updated_chapter_ids = []
        updated_challenge_ids = []

        old_star = doc['challenge_star'][str(challenge_id)]
        if star > old_star:
            MongoChallenge.db(self.server_id).update_one(
                {'_id': self.char_id},
                {
                    '$set': {'challenge_star.{0}'.format(challenge_id): star},
                    '$inc': {'chapters.{0}.star'.format(config.chapter): star - old_star}
                }
            )

            updated_chapter_ids.append(config.chapter)
            updated_challenge_ids.append(challenge_id)

            # open challenge, chapter
            for i in config.next:
                if str(i) in doc['challenge_star']:
                    continue

                updated_challenge_ids.append(i)

                MongoChallenge.db(self.server_id).update_one(
                    {'_id': self.char_id},
                    {'$set': {
                        'challenge_star.{0}'.format(i): 0,
                        'challenge_times.{0}'.format(i): 0
                    }}
                )

                chapter_id = ConfigChallengeMatch.get(i).chapter
                if str(chapter_id) in doc['chapters']:
                    continue

                updated_chapter_ids.append(chapter_id)
                MongoChallenge.db(self.server_id).update_one(
                    {'_id': self.char_id},
                    {'$set': {
                        'chapters.{0}'.format(chapter_id): {
                            'star': star,
                            'rewards': []
                        }
                    }}
                )

            self.send_chapter_notify(ids=updated_chapter_ids)
            self.send_challenge_notify(ids=updated_challenge_ids)

        # TODO drop
        drop = [(_id, _amount) for _id, _amount, _, _ in config.drop]
        Resource(self.server_id, self.char_id).add(drop, message="Challenge {0}".format(challenge_id))

        return drop

    def get_chapter_reward(self, chapter_id, index):
        config = ConfigChapter.get(chapter_id)
        # TODO error code

        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        doc = MongoChallenge.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'chapters.{0}'.format(chapter_id): 1}
        )

        try:
            this_chapter = doc['chapters'][str(chapter_id)]
        except KeyError:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if index in this_chapter['rewards']:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        need_star, item_id, item_amount = config.star_reward[index]
        if need_star > this_chapter['star']:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        Resource(self.server_id, self.char_id).add([(item_id, item_amount)])

        MongoChallenge.db(self.server_id).update_one(
            {'_id': self.char_id},
            {
                '$push': {
                    'chapters.{0}.rewards'.format(chapter_id): index
                }
            }
        )

        self.send_chapter_notify(ids=[chapter_id])
        return item_id, item_amount


    def buy_energy(self):
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

    def send_chapter_notify(self, ids=None):
        if ids:
            act = ACT_UPDATE
            projection = {'chapters.{0}'.format(i): 1 for i in ids}
        else:
            act = ACT_INIT
            projection = {'chapters': 1}

        doc = MongoChallenge.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

        notify = ChapterNotify()
        notify.act = act
        for _id, _info in doc['chapters'].iteritems():
            star = _info['star']
            rewards = _info['rewards']

            notify_chapter = notify.chapters.add()
            notify_chapter.id = int(_id)

            config = ConfigChapter.get(int(_id))
            for index in range(len(config.star_reward)):
                notify_chapter_reward = notify_chapter.rewards.add()
                notify_chapter_reward.index = index

                if index in rewards:
                    notify_chapter_reward.status = CHAPTER_REWARD_DONE
                else:
                    need_star = config.star_reward[index][0]
                    if star >= need_star:
                        notify_chapter_reward.status = CHAPTER_REWARD_OK
                    else:
                        notify_chapter_reward.status = CHAPTER_REWARD_NOT

        MessagePipe(self.char_id).put(msg=notify)

    def send_challenge_notify(self, ids=None):
        if ids:
            act = ACT_UPDATE
            projection = {'challenge_star.{0}'.format(i): 1 for i in ids}
            projection.update({'challenge_times.{0}'.format(i): 1 for i in ids})
        else:
            act = ACT_INIT
            projection = {'challenge_star': 1, 'challenge_times': 1}

        doc = MongoChallenge.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

        ids = doc['challenge_star'].keys()

        notify = ChallengeNotify()
        notify.act = act

        for i in ids:
            notify_challenge = notify.challenge.add()
            notify_challenge.id = int(i)
            notify_challenge.star = doc['challenge_star'][i]
            notify_challenge.remained_times = ConfigChallengeMatch.get(int(i)).times_limit - doc['challenge_times'].get(
                i, 0)

        MessagePipe(self.char_id).put(msg=notify)
