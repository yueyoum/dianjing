# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2015-07-15 11:41
Description:

"""

from dianjing.exception import GameException

from core.abstract import AbstractClub, AbstractStaff
from core.db import MongoDB
from core.club import Club
from core.match import ClubMatch

from core.signals import challenge_match_signal

from utils.message import MessagePipe
from config import ConfigChallengeMatch, ConfigStaff, ConfigErrorMessage

from protomsg.challenge_pb2 import ChallengeNotify


class ChallengeNPCStaff(AbstractStaff):
    def __init__(self, id, level, strength):
        super(ChallengeNPCStaff, self).__init__()

        self.id = id
        self.level = level

        config = ConfigStaff.get(id)
        self.race = config.race

        self.jingong = (config.jingong + config.jingong_grow * level) * strength
        self.qianzhi = (config.qianzhi + config.qianzhi_grow * level) * strength
        self.xintai = (config.xintai + config.xintai_grow * level) * strength
        self.baobing = (config.baobing + config.baobing_grow * level) * strength
        self.fangshou = (config.fangshou + config.fangshou_grow * level) * strength
        self.yunying = (config.yunying + config.yunying_grow * level) * strength
        self.yishi = (config.yishi + config.yishi_grow * level) * strength
        self.caozuo = (config.caozuo + config.caozuo_grow * level) * strength

        skills = config.skill_ids
        self.skills = {i: 1 for i in skills}


class ChallengeNPCClub(AbstractClub):
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
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = MongoDB.get(server_id)

        doc = self.mongo.character.find_one(
            {'_id': self.char_id},
            {'challenge_id': 1}
        )

        self.challenge_id = doc.get('challenge_id', None)
        if self.challenge_id is None:
            self.challenge_id = ConfigChallengeMatch.FIRST_ID
            self.mongo.character.update_one(
                {'_id': self.char_id},
                {'$set': {'challenge_id': self.challenge_id}}
            )


    def set_next_match_id(self):
        next_id = ConfigChallengeMatch.get(self.challenge_id).next_id
        self.mongo.character.update_one(
            {'_id': self.char_id},
            {'$set': {'challenge_id': next_id}}
        )
        return next_id


    def start(self):
        if not self.challenge_id:
            raise GameException(ConfigErrorMessage.get_error_id("CHALLENGE_ALL_FINISHED"))

        club_one = Club(self.server_id, self.char_id)
        club_two = ChallengeNPCClub(self.challenge_id)
        match = ClubMatch(club_one, club_two)

        msg = match.start()
        next_id = self.set_next_match_id()
        self.send_notify(challenge_id=next_id)

        challenge_match_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            challenge_id=self.challenge_id,
            win=msg.club_one_win,
        )

        return msg


    def send_notify(self, challenge_id=None):
        if challenge_id is None:
            challenge_id = self.challenge_id

        notify = ChallengeNotify()
        notify.id = challenge_id
        MessagePipe(self.char_id).put(msg=notify)
