# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       match
Date Created:   2015-05-21 15:08
Description:

"""

import random
from dianjing.exception import GameException
from config import ConfigErrorMessage

from protomsg.match_pb2 import ClubMatch as MessageClubMatch


class ClubMatch(object):
    # 俱乐部比赛
    def __init__(self, club_one, club_two):
        """

        :type club_one: core.abstract.AbstractClub
        :type club_two: core.abstract.AbstractClub
        """
        self.club_one = club_one
        self.club_two = club_two
        self.seed = random.randint(1, 10000)

        if not self.club_one.match_staffs_ready() or not self.club_two.match_staffs_ready():
            raise GameException(ConfigErrorMessage.get_error_id("MATCH_STAFF_NOT_READY"))

        self.club_one_fight_info = {}
        self.club_two_fight_info = {}
        self.club_one_winning_times = 0
        self.club_two_winning_times = 0

    @property
    def points(self):
        # 比分
        """

        :rtype : tuple
        """
        return self.club_one_winning_times, self.club_two_winning_times

    def start(self):
        msg = MessageClubMatch()
        msg.club_one.MergeFrom(self.club_one.make_protomsg())
        msg.club_two.MergeFrom(self.club_two.make_protomsg())
        msg.seed = self.seed

        for i in range(5):
            staff_one = self.club_one.staffs[self.club_one.match_staffs[i]]
            staff_two = self.club_two.staffs[self.club_two.match_staffs[i]]

            msg_match = msg.match.add()
            msg_match.staff_one.id = staff_one.id
            msg_match.staff_one.caozuo = int(staff_one.caozuo)
            msg_match.staff_one.jingying = int(staff_one.jingying)
            msg_match.staff_one.baobing = int(staff_one.baobing)
            msg_match.staff_one.zhanshu = int(staff_one.zhanshu)
            msg_match.staff_one.skills.extend(staff_one.skills.keys())
            msg_match.staff_one.power = staff_one.power

            msg_match.staff_two.id = staff_two.id
            msg_match.staff_two.caozuo = int(staff_two.caozuo)
            msg_match.staff_two.jingying = int(staff_two.jingying)
            msg_match.staff_two.baobing = int(staff_two.baobing)
            msg_match.staff_two.zhanshu = int(staff_two.zhanshu)
            msg_match.staff_two.skills.extend(staff_two.skills.keys())
            msg_match.staff_two.power = staff_two.power

        return msg
