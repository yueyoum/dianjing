# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       match
Date Created:   2015-05-21 15:08
Description:

"""

import random
from dianjing.exception import GameException

from config import ConfigUnit, ConfigPolicy, ConfigErrorMessage, ConfigSkill

from protomsg.match_pb2 import ClubMatch as MessageClubMatch
from protomsg.match_pb2 import StaffMatch as MessageStaffMatch


#
# class MatchUnit(object):
#     UNIT = {}
#     # UNIT = {
#     #   race_id: [round_one, round_two, round_three],
#     # }
#     # round = [staff_id, staff_id, staff_id...]
#     # round 长度为 可出兵种的 总触发概率
#     # 其中元素类似这样 [1,1,1, 2,2, 3,3,3,3,3]
#     # 表示 1 有 3 的几率， 2 有 2 的几率，一次类推
#     # round[ random.randint(0, length(round)) ] 即可按照概率随机选出一个兵种
#
#     @classmethod
#     def init(cls):
#         if cls.UNIT:
#             return
#
#         for u in ConfigUnit.all_values():
#             if u.race in cls.UNIT:
#                 cls.UNIT[u.race].append(u)
#             else:
#                 cls.UNIT[u.race] = [u]
#
#         for race_id, units in cls.UNIT.iteritems():
#             round_one = []
#             round_two = []
#             round_three = []
#
#             for u in units:
#                 round_one.extend([u.id] * u.first_trig)
#                 round_two.extend([u.id] * u.second_trig)
#                 round_three.extend([u.id] * u.third_trig)
#
#             cls.UNIT[race_id] = [round_one, round_two, round_three]
#
#     @classmethod
#     def get(cls, race, round_index):
#         # 根据种族和第几回合来随机选择兵种
#         units = cls.UNIT[race][round_index]
#         index = random.randint(0, len(units) - 1)
#         return units[index]
#
#
# class OneMatch(object):
#     def __init__(self, staff_one, staff_two, policy_one, policy_two):
#         """
#         :type staff_one: core.abstract.AbstractStaff
#         :type staff_two: core.abstract.AbstractStaff
#         """
#         MatchUnit.init()
#
#         self.staff_one = staff_one
#         self.staff_two = staff_two
#         self.policy_one = policy_one
#         self.policy_two = policy_two
#
#         self.advantage_one = 50
#         self.advantage_two = 50
#
#         self.round_index = 0
#         self.winning = None
#
#     def round(self):
#         msg = MessageRound()
#         msg.round_index = self.round_index
#
#         unit_one = MatchUnit.get(self.staff_one.race, self.round_index)
#         unit_two = MatchUnit.get(self.staff_two.race, self.round_index)
#
#         msg.staff_one.unit_id = unit_one
#         msg.staff_one.advantage_begin = int(self.advantage_one)
#
#         msg.staff_two.unit_id = unit_two
#         msg.staff_two.advantage_begin = int(self.advantage_two)
#
#         def calculate(staff, unit_id):
#             """
#
#             :type staff: core.abstract.AbstractStaff
#             :type unit_id: int
#             """
#
#             # TODO new property
#             base_attribute = random.randint(20, 100)
#
#             # base_attribute = staff.jingong + staff.baobing + staff.caozuo + \
#             #                  staff.qianzhi + staff.fangshou + staff.yunying
#             # base_attribute = base_attribute * staff.xintai / 1000 * 1
#
#             # skill_id = ConfigUnit.get(unit_id).skill
#             # config_skill = ConfigSkill.get(skill_id)
#             #
#             # skill_addition = 0
#             # for name, percent in config_skill.addition_ids:
#             #     skill_addition += getattr(staff, name) * percent / 100.0
#             #
#             # skill_addition *= 1
#             #
#             # skill_strength = (config_skill.value_base + staff.skills.get(skill_id, 0) * config_skill.level_grow) / 10
#             # # skill_strength = skill_addition * skill_strength * staff.yishi / 1000 * 1
#             #
#             # return base_attribute + skill_strength
#             return base_attribute
#
#         a = calculate(self.staff_one, unit_one)
#         b = calculate(self.staff_two, unit_two)
#
#         y = ((a - b) / (a + b)) * 100
#         advantage_change = abs(y) / 2
#
#         if y < 0:
#             self.advantage_one -= advantage_change
#             self.advantage_two += advantage_change
#         else:
#             self.advantage_one += advantage_change
#             self.advantage_two -= advantage_change
#
#         # policy addition
#         config_policy = ConfigPolicy.get(self.policy_one)
#         if config_policy.advantage_add_round == self.round_index:
#             self.advantage_one += config_policy.advantage_add_value
#             self.advantage_two -= config_policy.advantage_add_value
#
#         config_policy = ConfigPolicy.get(self.policy_two)
#         if config_policy.advantage_add_round == self.round_index:
#             self.advantage_two += config_policy.advantage_add_value
#             self.advantage_one -= config_policy.advantage_add_value
#
#         msg.staff_one.advantage_end = int(self.advantage_one)
#         msg.staff_two.advantage_end = int(self.advantage_two)
#
#         # round to 100
#         diff = 100 - (msg.staff_one.advantage_end + msg.staff_two.advantage_end)
#         if diff:
#             if msg.staff_one.advantage_end >= msg.staff_two.advantage_end:
#                 msg.staff_one.advantage_end += diff
#             else:
#                 msg.staff_two.advantage_end += diff
#
#         return msg
#
#     def start(self):
#         msg = MessageOneMatch()
#
#         for i in range(1, 4):
#             round_msg = self.round()
#             msg_round = msg.rounds.add()
#             msg_round.MergeFrom(round_msg)
#
#             if self.advantage_one >= 90:
#                 self.winning = self.staff_one
#                 break
#
#             if self.advantage_one <= 10:
#                 self.winning = self.staff_two
#                 break
#
#             self.round_index += 1
#
#         if not self.winning:
#             if self.advantage_one >= self.advantage_two:
#                 rate = (self.advantage_two / 100.0) ** 2 * 100
#                 if random.randint(0, 100) <= rate:
#                     self.winning = self.staff_two
#                 else:
#                     self.winning = self.staff_one
#             else:
#                 rate = (self.advantage_one / 100.0) ** 2 * 100
#                 if random.randint(0, 100) <= rate:
#                     self.winning = self.staff_one
#                 else:
#                     self.winning = self.staff_two
#
#         msg.staff_one_win = self.winning is self.staff_one
#         return msg
#
#
# class StaffMatch(object):
#     def __init__(self, staff_one, staff_two, policy_one, policy_two):
#         """
#         :type staff_one: core.abstract.AbstractStaff
#         :type staff_two: core.abstract.AbstractStaff
#         """
#
#         self.staff_one = staff_one
#         self.staff_two = staff_two
#         self.policy_one = policy_one
#         self.policy_two = policy_two
#
#     def start(self):
#         msg = MessageStaffMatch()
#         msg.staff_one_id = self.staff_one.id
#         msg.staff_two_id = self.staff_two.id
#
#         match_times = 5
#         staff_one_win_times = 0
#
#         for i in range(match_times):
#             one_match = OneMatch(self.staff_one, self.staff_two, self.policy_one, self.policy_two)
#             one_msg = one_match.start()
#
#             msg_match = msg.match.add()
#             msg_match.MergeFrom(one_msg)
#
#             if one_msg.staff_one_win:
#                 staff_one_win_times += 1
#
#         if staff_one_win_times > match_times / 2:
#             msg.staff_one_win = True
#         else:
#             msg.staff_one_win = False
#
#         return msg


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
            msg_match.staff_one.caozuo = staff_one.caozuo
            msg_match.staff_one.jingying = staff_one.jingying
            msg_match.staff_one.baobing = staff_one.baobing
            msg_match.staff_one.zhanshu = staff_one.zhanshu
            msg_match.staff_one.skills.extend(staff_one.skills.keys())
            
            msg_match.staff_two.id = staff_two.id
            msg_match.staff_two.caozuo = staff_two.caozuo
            msg_match.staff_two.jingying = staff_two.jingying
            msg_match.staff_two.baobing = staff_two.baobing
            msg_match.staff_two.zhanshu = staff_two.zhanshu
            msg_match.staff_two.skills.extend(staff_two.skills.keys())

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
    def __init__(self, rival, win):
        self.rival = rival
        self.win = win
