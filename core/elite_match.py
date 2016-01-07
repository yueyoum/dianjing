# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       elite_match
Date Created:   2015-12-10 11:35
Description:

"""

import arrow

from dianjing.exception import GameException

from core.mongo import MongoEliteMatch, MongoCharacter
from core.abstract import AbstractClub, AbstractStaff
from core.club import Club
from core.match import ClubMatch
from core.package import Drop
from core.resource import Resource
from core.character import Character
from core.staff import StaffManger
from core.challenge import Challenge

from utils.message import MessagePipe

from config import ConfigEliteArea, ConfigEliteMatch, ConfigErrorMessage, ConfigStaff

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.elite_match_pb2 import (
    EliteNotify
)


ELITE_MATCH_COST = 5


class EliteNPCStaff(AbstractStaff):
    __slots__ = []

    def __init__(self, _id, level):
        super(EliteNPCStaff, self).__init__()

        self.id = _id
        self.level = level

        config = ConfigStaff.get(_id)
        self.race = config.race
        self.skills = {i: 1 for i in config.skill_ids}

        self.luoji = config.luoji
        self.minjie = config.minjie
        self.lilun = config.lilun
        self.wuxing = config.wuxing
        self.meili = config.meili

        self.calculate_secondary_property()


class EliteNPCClub(AbstractClub):
    __slots__ = []

    def __init__(self, elite_match_id):
        super(EliteNPCClub, self).__init__()

        config = ConfigEliteMatch.get(elite_match_id)

        self.id = elite_match_id

        self.match_staffs = config.staffs
        self.policy = config.policy
        self.name = config.club_name
        self.flag = config.club_flag

        for i in self.match_staffs:
            self.staffs[i] = EliteNPCStaff(i, config.staff_level)

        self.qianban_affect()


def get_next_restore_timestamp():
    now = arrow.utcnow()
    next_hour = now.replace(hours=1)

    next_hour = arrow.Arrow(
        next_hour.year,
        next_hour.month,
        next_hour.day,
        next_hour.hour,
        0,
        0,
        0,
        tzinfo=next_hour.tzinfo
    )

    return next_hour.timestamp


class EliteMatch(object):
    __slots__ = ['server_id', 'char_id', 'cur_times']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        doc = MongoEliteMatch.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'cur_times': 1}
        )

        if not doc:
            doc = MongoEliteMatch.document()
            doc['_id'] = self.char_id
            MongoEliteMatch.db(self.server_id).insert_one(doc)

        self.cur_times = doc['cur_times']

    @classmethod
    def cronjob_clean_match_times(cls, server_id):
        for char_id in Character.get_recent_login_char_ids(server_id):
            doc = MongoEliteMatch.db(server_id).find_one({'_id': char_id})

            updater = {}
            for area_id, area_info in doc['areas'].iteritems():
                for ch_id, ch_info in area_info['challenges']:
                    key = 'areas.{0}.challenges.{1}.times'.format(area_id, ch_id)
                    updater[key] = ConfigEliteMatch.get(int(ch_id)).max_times

            MongoEliteMatch.db(server_id).update_one(
                {'_id': char_id},
                {'$set': updater}
            )

    def open_area(self, aid, send_notify=True):
        config = ConfigEliteArea.get(aid)
        if not config:
            return

        doc = MongoEliteMatch.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'areas.{0}'.format(aid): 1}
        )

        if str(aid) in doc['areas']:
            return

        updater = {
            'areas.{0}'.format(aid): {
                str(config.first_match_id()): 0
            }
        }

        MongoEliteMatch.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        # if send_notify:
        #     self.send_notify(area_id=aid)

    # def cost_cur_times(self):
    #     if self.cur_times <= 0:
    #         raise GameException(ConfigErrorMessage.get_error_id("ELITE_TOTAL_NO_TIMES"))
    #
    #     self.cur_times -= 1
    #     # TODO lock
    #     MongoEliteMatch.db(self.server_id).update_one(
    #         {'_id': self.char_id},
    #         {'$set': {'cur_times': self.cur_times}}
    #     )
    #
    #     self.send_times_notify()

    def start(self, area_id, challenge_id):
        # 判断大区是否存在
        if not ConfigEliteArea.get(area_id):
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_AREA_NOT_EXIST"))

        # 获取玩家数据
        doc = MongoEliteMatch.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'areas.{0}.challenges.{1}'.format(area_id, challenge_id): 1}
        )

        # 判断大区是否已开启
        if not doc['areas'].get(str(area_id), {}):
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_AREA_NOT_OPEN"))

        # 判断是否已开方关卡
        elite = doc['areas']['challenges'].get(str(challenge_id), {})
        if not elite:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_NOT_OPEN"))

        # 挑战次数检查
        if elite.get('times', 0) >= ConfigEliteMatch.get(challenge_id):
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_WITHOUT_TIMES"))

        # 体力检查
        doc_char = MongoCharacter.db(self.server_id).find_one({'_id': self.char_id}, {'energy': 1})
        if doc_char['energy']['power'] < ELITE_MATCH_COST:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_NOT_ENOUGH_ENERGY"))

        # match
        club_one = Club(self.server_id, self.char_id)
        club_two = EliteNPCClub(challenge_id)
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
        StaffManger(self.server_id, self.char_id).update_winning_rate(result, win_club == club_one)

        # 扣除能量
        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {'energy.power': -ELITE_MATCH_COST}}
        )

        # 检查重能
        Challenge(self.server_id, self.char_id).check_energize()

        # 更新挑战次数
        updater = {'areas.{0}.{1}.times'.format(area_id, challenge_id): 1}
        MongoEliteMatch.db(self.server_id).update_one(
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
            doc = MongoEliteMatch.db(self.server_id).find_one(
                {'_id': self.char_id}, {'areas.{0}'.format(area_id): 1}
            )

            setter = {}
            # 判断是否需要更新星级
            if stars > doc['areas'][area_id].get(challenge_id, {}).get('stars', 0):
                setter['areas.{0}.{1}.stars'.format(area_id, challenge_id)] = stars

            next_challenge_id = int(challenge_id) + 1
            next_area_id = int(area_id) + 1

            # 如果下一关存在
            if ConfigEliteMatch.get(next_challenge_id):
                # 如果是下一大区的， 开启新大区
                if ConfigEliteArea.get(int(area_id) + 1) <= next_challenge_id:
                    setter['areas.{0}.{1}'.format(next_area_id, next_challenge_id)] = {'stars': 0,
                                                                                       'times': 0,
                                                                                       'packages': []}
                # 如果是当前大区的， 开启
                else:
                    setter['areas.{0}.{1}'.format(area_id, next_challenge_id)] = {'stars': 0,
                                                                                  'times': 0,
                                                                                  'packages': []}
            # 更新数据
            if setter:
                MongoEliteMatch.db(self.server_id).update_one(
                    {'_id': self.char_id},
                    {'$set': setter}
                )

            # 同步到客户端
            self.challenge_notify(act=ACT_UPDATE)

            # 通关奖励
            drop = Drop.generate(ConfigEliteMatch.get(int(challenge_id)).reward)
            Resource(self.server_id, self.char_id).save_drop(drop)
            return drop.make_protomsg()

        # # send signal
        # challenge_match_signal.send(
        #     sender=None,
        #     server_id=self.server_id,
        #     char_id=self.char_id,
        #     challenge_id=int(challenge_id),
        #     win=(win_club == club_one),
        # )

        return None

    def star_reward(self, area_id, index):
        pass

    # def send_notify(self, area_id=None, match_id=None):
    #     if area_id:
    #         act = ACT_UPDATE
    #         area_ids = [area_id]
    #     else:
    #         act = ACT_INIT
    #         area_ids = ConfigEliteArea.INSTANCES.keys()
    #
    #     def get_match_ids(_aid):
    #         if area_id:
    #             if match_id:
    #                 return [match_id]
    #             return ConfigEliteArea.get(area_id).match_ids
    #
    #         return ConfigEliteArea.get(_aid).match_ids
    #
    #     doc = MongoEliteMatch.db(self.server_id).find_one({'_id': self.char_id})
    #
    #     notify = EliteNotify()
    #     notify.act = act
    #     for aid in area_ids:
    #         notify_area = notify.area.add()
    #         notify_area.id = aid
    #
    #         matchs = doc['areas'].get(str(aid), {})
    #         if not matchs:
    #             notify_area.status = ELITE_AREA_NOT_OPEN
    #             continue
    #
    #         if set([int(i) for i in matchs]) == set(ConfigEliteArea.get(aid).match_ids):
    #             notify_area.status = ELITE_AREA_FINISH
    #         else:
    #             notify_area.status = ELITE_AREA_OPEN
    #
    #         for mid in get_match_ids(aid):
    #             cur_times = matchs.get(str(mid), -1)
    #
    #             notify_area_match = notify_area.match.add()
    #             notify_area_match.id = mid
    #             notify_area_match.cur_times = cur_times
    #     MessagePipe(self.char_id).put(msg=notify)

    def challenge_notify(self, act=ACT_INIT):
        doc = MongoEliteMatch.db(self.server_id).find_one({'_id': self.char_id})

        notify = EliteNotify()
        notify.act = act
        for k, v in doc['areas'].iteritems():
            notify_area = notify.area.add()
            notify_area.id = k
            notify_area.package_one = v['packages']['1']
            notify_area.package_two = v['packages']['2']
            notify_area.package_three = v['packages']['3']

            for challenge_id, info in v['challenges'].iteritems():
                notify_challenge = notify_area.challenge.add()
                notify_challenge.id = challenge_id
                notify_challenge.times = info['times']
                notify_challenge.stars = info['stars']

        MessagePipe(self.char_id).put(msg=notify)