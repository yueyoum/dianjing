# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2015-07-15 11:41
Description:

"""

from dianjing.exception import GameException

from core.abstract import AbstractClub, AbstractStaff
from core.mongo import MongoCharacter
from core.club import Club
from core.match import ClubMatch
from core.package import Drop
from core.resource import Resource

from core.signals import challenge_match_signal

from utils.message import MessagePipe
from config import ConfigChallengeMatch, ConfigStaff, ConfigErrorMessage

from protomsg.challenge_pb2 import ChallengeNotify


class ChallengeNPCStaff(AbstractStaff):
    __slots__ = []
    def __init__(self, _id, level, strength):
        super(ChallengeNPCStaff, self).__init__()

        self.id = _id
        self.level = level

        config = ConfigStaff.get(_id)
        self.race = config.race

        self.jingong = (config.jingong + config.jingong_grow * (level - 1)) * strength
        self.qianzhi = (config.qianzhi + config.qianzhi_grow * (level - 1)) * strength
        self.xintai = (config.xintai + config.xintai_grow * (level - 1)) * strength
        self.baobing = (config.baobing + config.baobing_grow * (level - 1)) * strength
        self.fangshou = (config.fangshou + config.fangshou_grow * (level - 1)) * strength
        self.yunying = (config.yunying + config.yunying_grow * (level - 1)) * strength
        self.yishi = (config.yishi + config.yishi_grow * (level - 1)) * strength
        self.caozuo = (config.caozuo + config.caozuo_grow * (level - 1)) * strength

        skills = config.skill_ids
        self.skills = {i: 1 for i in skills}


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


class Challenge(object):
    __slots__ = ['server_id', 'char_id', 'challenge_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        doc = MongoCharacter.db(server_id).find_one(
            {'_id': self.char_id},
            {'challenge_id': 1}
        )

        self.challenge_id = doc.get('challenge_id', None)
        if self.challenge_id is None:
            self.challenge_id = ConfigChallengeMatch.FIRST_ID
            MongoCharacter.db(server_id).update_one(
                {'_id': self.char_id},
                {'$set': {'challenge_id': self.challenge_id}}
            )

    def current_challenge_id(self):
        if self.challenge_id == ConfigChallengeMatch.FIRST_ID:
            return 0
        return self.challenge_id - 1

    def set_next_match_id(self):
        if self.challenge_id == ConfigChallengeMatch.LAST_ID:
            next_id = 0
        else:
            next_id = self.challenge_id + 1
        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'challenge_id': next_id}}
        )
        return next_id

    def start(self):
        if not self.challenge_id:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_ALL_FINISHED"))

        club_one = Club(self.server_id, self.char_id)
        if club_one.current_level() < ConfigChallengeMatch.get(self.challenge_id).need_club_level:
            raise GameException(ConfigErrorMessage.get_error_id("CLUB_LEVEL_NOT_ENOUGH"))

        club_two = ChallengeNPCClub(self.challenge_id)
        match = ClubMatch(club_one, club_two)

        msg = match.start()

        challenge_match_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            challenge_id=self.challenge_id,
            win=msg.club_one_win,
        )

        if not msg.club_one_win:
            return msg, None

        next_id = self.set_next_match_id()
        self.send_notify(challenge_id=next_id)

        drop = Drop.generate(ConfigChallengeMatch.get(self.challenge_id).package)
        message = u"Drop from challenge {0}".format(self.challenge_id)
        Resource(self.server_id, self.char_id).save_drop(drop, message=message)

        return msg, drop.make_protomsg()

    def send_notify(self, challenge_id=None):
        if challenge_id is None:
            challenge_id = self.challenge_id

        notify = ChallengeNotify()
        notify.id = challenge_id
        MessagePipe(self.char_id).put(msg=notify)
