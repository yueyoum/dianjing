# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       match
Date Created:   2015-05-21 15:08
Description:

"""

import random
from dianjing.exception import GameException

from config import ConfigUnit, ConfigPolicy, ConfigErrorMessage, ConfigSkill, ConfigStaff

from protomsg.match_pb2 import ClubMatch as MessageClubMatch
from protomsg.match_pb2 import Match as MessageMatch
from protomsg.match_pb2 import Round as MessageRound


class MatchUnit(object):
    UNIT = {}
    # UNIT = {
    #   race_id: [round_one, round_two, round_three],
    # }
    # round = [staff_id, staff_id, staff_id...]
    # round 长度为 可出兵种的 总触发概率
    # 其中元素类似这样 [1,1,1, 2,2, 3,3,3,3,3]
    # 表示 1 有 3 的几率， 2 有 2 的几率，一次类推
    # round[ random.randint(0, length(round)) ] 即可按照概率随机选出一个兵种

    @classmethod
    def init(cls):
        if cls.UNIT:
            return

        for u in ConfigUnit.all_values():
            if u.race in cls.UNIT:
                cls.UNIT[u.race].append(u)
            else:
                cls.UNIT[u.race] = [u]

        for race_id, units in cls.UNIT.iteritems():
            round_one = []
            round_two = []
            round_three = []

            for u in units:
                round_one.extend([u.id] * u.first_trig)
                round_two.extend([u.id] * u.second_trig)
                round_three.extend([u.id] * u.third_trig)

            cls.UNIT[race_id] = [round_one, round_two, round_three]

    @classmethod
    def get(cls, race, round_index):
        # 根据种族和第几回合来随机选择兵种
        units = cls.UNIT[race][round_index]
        index = random.randint(0, len(units) - 1)
        return units[index]


class Match(object):
    # 一场比赛
    def __init__(self, staff_one, staff_two, policy_one, policy_two):
        """
        :type staff_one: core.abstract.AbstractStaff
        :type staff_two: core.abstract.AbstractStaff
        """
        MatchUnit.init()

        self.staff_one = staff_one
        self.staff_two = staff_two
        self.policy_one = policy_one
        self.policy_two = policy_two

        self.advantage_one = 50
        self.advantage_two = 50

        self.round_index = 0
        self.winning = None

    def round(self):
        msg = MessageRound()
        msg.round_index = self.round_index

        unit_one = MatchUnit.get(self.staff_one.race, self.round_index)
        unit_two = MatchUnit.get(self.staff_two.race, self.round_index)

        msg.staff_one.unit_id = unit_one
        msg.staff_one.advantage_begin = int(self.advantage_one)

        msg.staff_two.unit_id = unit_two
        msg.staff_two.advantage_begin = int(self.advantage_two)

        def calculate(staff, unit_id):
            """

            :type staff: core.abstract.AbstractStaff
            :type unit_id: int
            """

            p = staff.jingong + staff.baobing + staff.caozuo + staff.qianzhi + staff.fangshou + staff.yunying

            skill_id = ConfigUnit.get(unit_id).skill
            if skill_id not in staff.skills:
                j = 0
            else:
                config_skill = ConfigSkill.get(skill_id)

                x = 0
                for name, percent in config_skill.addition_ids:
                    x += getattr(staff, name) * percent / 100.0

                m = (config_skill.value_base + (staff.skills[skill_id] - 1) * config_skill.level_grow) / 100.0
                j = (staff.xintai + staff.yishi + x) * m

            return (p, j)

        pone, jone = calculate(self.staff_one, unit_one)
        ptwo, jtwo = calculate(self.staff_two, unit_two)

        s = pone + jone + ptwo + jtwo

        y = (((pone + jone) - (ptwo + jtwo)) / float(s)) * 100

        if y < 0:
            self.advantage_one -= abs(y)
            self.advantage_two += abs(y)
        else:
            self.advantage_one += abs(y)
            self.advantage_two -= abs(y)


        # policy addition
        config_policy = ConfigPolicy.get(self.policy_one)
        if config_policy.advantage_add_round == self.round_index:
            self.advantage_one += config_policy.advantage_add_value

        config_policy = ConfigPolicy.get(self.policy_two)
        if config_policy.advantage_add_round == self.round_index:
            self.advantage_two += config_policy.advantage_add_value

        msg.staff_one.advantage_end = int(self.advantage_one)
        msg.staff_two.advantage_end = int(self.advantage_two)

        return msg

    def start(self):
        msg = MessageMatch()
        msg.staff_one_id = self.staff_one.id
        msg.staff_two_id = self.staff_two.id

        for i in range(1, 4):
            round_msg = self.round()
            msg_round = msg.rounds.add()
            msg_round.MergeFrom(round_msg)

            if self.advantage_one >= 90:
                self.winning = self.staff_one
                break

            if self.advantage_one <= 10:
                self.winning = self.staff_two
                break

            self.round_index += 1

        if not self.winning:
            if self.advantage_one >= self.advantage_two:
                rate = (self.advantage_two / 100.0) ** 2 * 100
                if random.randint(0, 100) <= rate:
                    self.winning = self.staff_two
                else:
                    self.winning = self.staff_one
            else:
                rate = (self.advantage_one / 100.0) ** 2 * 100
                if random.randint(0, 100) <= rate:
                    self.winning = self.staff_one
                else:
                    self.winning = self.staff_two

        msg.staff_one_win = self.winning is self.staff_one
        return msg


class ClubMatch(object):
    # 俱乐部比赛
    def __init__(self, club_one, club_two):
        """

        :type club_one: core.abstract.AbstractClub
        :type club_two: core.abstract.AbstractClub
        """
        self.club_one = club_one
        self.club_two = club_two

        if not self.club_one.match_staffs_ready() or not self.club_two.match_staffs_ready():
            raise GameException(ConfigErrorMessage.get_error_id("MATCH_STAFF_NOT_READY"))

        self.club_one_fight_info = {}
        self.club_two_fight_info = {}

    def start(self):
        msg = MessageClubMatch()
        msg.club_one.MergeFrom(self.club_one.make_protomsg())
        msg.club_two.MergeFrom(self.club_two.make_protomsg())

        club_one_winning_times = 0
        club_two_winning_times = 0

        for i in range(5):
            staff_one = self.club_one.staffs[self.club_one.match_staffs[i]]
            staff_two = self.club_two.staffs[self.club_two.match_staffs[i]]

            match = Match(staff_one, staff_two, self.club_one.policy, self.club_two.policy)
            match_msg = match.start()

            msg_match = msg.match.add()
            msg_match.MergeFrom(match_msg)

            if match_msg.staff_one_win:
                club_one_winning_times += 1
            else:
                club_two_winning_times += 1

            self.club_one_fight_info[staff_one.id] = FightInfo(staff_two.id, match_msg.staff_one_win)
            self.club_two_fight_info[staff_two.id] = FightInfo(staff_one.id, not match_msg.staff_one_win)

        if club_one_winning_times >= 3:
            msg.club_one_win = True
        else:
            msg.club_one_win = False

        return msg

    def get_club_one_fight_info(self):
        """

        :rtype : dict[int, FightInfo]
        """
        return self.club_one_fight_info

    def get_club_two_fight_info(self):
        """
        
        :rtype: dict[int, FightInfo]
        """
        return self.club_two_fight_info


class FightInfo(object):
    def __init__(self, rival, win=False):
        self.riva = rival
        self.win = win


