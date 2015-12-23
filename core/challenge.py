# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2015-07-15 11:41
Description:

"""

from dianjing.exception import GameException

from core.abstract import AbstractClub, AbstractStaff
from core.mongo import MongoChallenge
from core.club import Club
from core.match import ClubMatch
from core.package import Drop
from core.resource import Resource

from core.signals import challenge_match_signal

from utils.message import MessagePipe
from config import ConfigChallengeType, ConfigChallengeMatch, ConfigStaff, ConfigErrorMessage

from protomsg.challenge_pb2 import ChallengeNotify, CHALLENGE_FINISH, CHALLENGE_NOT_OPEN, CHALLENGE_OPEN


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
            doc['area_id'] = 1
            doc['areas'] = {'1': 1}
            MongoChallenge.db(self.server_id).insert_one(doc)

    def current_challenge_id(self):
        doc = MongoChallenge.db(self.server_id).find_one({'_id': self.char_id})
        challenge_ids = []
        for aid, cid in doc['areas'].iteritems():
            if cid == 0:
                cid = ConfigChallengeType.end_challenge_id(int(aid))

            challenge_ids.append(cid)

        return max(challenge_ids)

    def set_next(self, area_id, challenge_id):
        if challenge_id == ConfigChallengeType.end_challenge_id(area_id):
            challenge_id = 0
        else:
            challenge_id += 1

        updater = {
            'areas.{0}'.format(area_id): challenge_id
        }

        opened_area_ids = ConfigChallengeType.opened_area_ids(challenge_id)
        for i in opened_area_ids:
            updater['areas.{0}'.format(i)] = ConfigChallengeType.start_challenge_id(i)

        MongoChallenge.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        self.send_notify()

    def switch_area(self, area_id):
        if not ConfigChallengeType.get(area_id):
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_AREA_NOT_EXIST"))

        MongoChallenge.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'area_id': area_id}}
        )

        self.send_notify()

    def start(self, area_id):
        if not ConfigChallengeType.get(area_id):
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_AREA_NOT_EXIST"))

        doc = MongoChallenge.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'areas.{0}'.format(area_id): 1}
        )

        challenge_id = doc['areas'].get(str(area_id), None)
        if challenge_id is None:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_AREA_NOT_OPEN"))

        if challenge_id == 0:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_AREA_FINISH"))

        club_one = Club(self.server_id, self.char_id)
        if club_one.current_level() < ConfigChallengeMatch.get(challenge_id).need_club_level:
            raise GameException(ConfigErrorMessage.get_error_id("CLUB_LEVEL_NOT_ENOUGH"))

        club_two = ChallengeNPCClub(challenge_id)
        match = ClubMatch(club_one, club_two)

        msg = match.start()

        # if msg.club_one_win:
        #     self.set_next(area_id, challenge_id)
        #
        #     drop = Drop.generate(ConfigChallengeMatch.get(challenge_id).package)
        #     message = u"Drop from challenge {0}".format(challenge_id)
        #     Resource(self.server_id, self.char_id).save_drop(drop, message=message)
        # else:
        #     drop = Drop()
        #
        # challenge_match_signal.send(
        #     sender=None,
        #     server_id=self.server_id,
        #     char_id=self.char_id,
        #     challenge_id=challenge_id,
        #     win=msg.club_one_win,
        # )

        return msg, Drop().make_protomsg()

    def send_notify(self):
        doc = MongoChallenge.db(self.server_id).find_one({'_id': self.char_id})
        area_ids = ConfigChallengeType.INSTANCES.keys()

        notify = ChallengeNotify()
        notify.current_area_id = doc['area_id']

        for i in area_ids:
            notify_area = notify.area.add()
            notify_area.id = i

            challenge_id = doc['areas'].get(str(i), None)
            if challenge_id is None:
                notify_area.status = CHALLENGE_NOT_OPEN
            elif challenge_id == 0:
                notify_area.status = CHALLENGE_FINISH
            else:
                notify_area.status = CHALLENGE_OPEN
                notify_area.challenge_id = challenge_id

        MessagePipe(self.char_id).put(msg=notify)
