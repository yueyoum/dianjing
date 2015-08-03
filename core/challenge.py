# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2015-07-15 11:41
Description:

"""

from dianjing.exception import GameException

from core.abstract import AbstractClub, AbstractStaff
from core.db import get_mongo_db
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

        config_staff = ConfigStaff.get(id)
        self.race = config_staff.race

        self.jingong = (config_staff.jingong + config_staff.jingong_grow * level) * strength
        self.qianzhi = (config_staff.qianzhi + config_staff.qianzhi_grow * level) * strength
        self.xintai = (config_staff.xintai + config_staff.xintai_grow * level) * strength
        self.baobing = (config_staff.baobing + config_staff.baobing_grow * level) * strength
        self.fangshou = (config_staff.fangshou + config_staff.fangshou_grow * level) * strength
        self.yunying = (config_staff.yunying + config_staff.yunying_grow * level) * strength
        self.yishi = (config_staff.yishi + config_staff.yishi_grow * level) * strength
        self.caozuo = (config_staff.caozuo + config_staff.caozuo_grow * level) * strength

        self.skills = []


class ChallengeNPCClub(AbstractClub):
    def __init__(self, challenge_match_id):
        super(ChallengeNPCClub, self).__init__()

        level = ConfigChallengeMatch.get(challenge_match_id).level
        strength = ConfigChallengeMatch.get(challenge_match_id).strength

        self.id = challenge_match_id

        config = ConfigChallengeMatch.get(challenge_match_id)
        self.match_staffs = config.staffs
        self.policy = config.policy
        self.name = config.club_name
        self.flag = config.club_flag

        for i in self.match_staffs:
            self.staffs[i] = ChallengeNPCStaff(i, level, strength)



class Challenge(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = get_mongo_db(server_id)

    def get_match_id(self):
        char = self.mongo.character.find_one({'_id': self.char_id}, {'challenge_id': 1})
        challenge_id = char.get('challenge_id', None)
        if challenge_id is None:
            challenge_id = ConfigChallengeMatch.FIRST_ID
            self.mongo.character.update_one(
                {'_id': self.char_id},
                {'$set': {'challenge_id': challenge_id}}
            )

        return challenge_id

    def set_next_match_id(self, challenge_id):
        next_id = ConfigChallengeMatch.get(challenge_id).next_id
        self.mongo.character.update_one(
            {'_id': self.char_id},
            {'$set': {'challenge_id': next_id}}
        )
        return next_id


    def start(self):
        challenge_id = self.get_match_id()
        if not challenge_id:
            # TODO all finished!
            raise RuntimeError("all finished!")

        club_one = Club(self.server_id, self.char_id)

        if not club_one.match_staffs_ready():
            raise GameException( ConfigErrorMessage.get_error_id("MATCH_STAFF_NOT_READY") )

        club_two = ChallengeNPCClub(challenge_id)
        match = ClubMatch(club_one, club_two)

        msg = match.start()
        next_id = self.set_next_match_id(challenge_id)
        self.send_notify(challenge_id=next_id)

        challenge_match_signal.send(
            sender=None,
            server_id=self.server_id,
            char_id=self.char_id,
            challenge_id=challenge_id,
            win=msg.club_one_win,
        )

        return msg


    def send_notify(self, challenge_id=None):
        if challenge_id is None:
            challenge_id = self.get_match_id()

        notify = ChallengeNotify()
        notify.id = challenge_id
        MessagePipe(self.char_id).put(msg=notify)

