# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       battle
Date Created:   2015-05-21 15:08
Description:

"""

import random


from apps.staff.core import Staff

from config import CONFIG


class Unit(object):
    UNIT = {}
    # UNIT = {
    #   race_id: [round_one, round_two, round_three],
    # }
    # round = [staff_id, staff_id, staff_id...]
    # round 长度为 可出兵种的 总触发概率
    # 其中元素类似这样 [1,1,1, 2,2, 3,3,3,3,3]
    # 表示 1 有 3 的几率， 2 有 2 的几率，一次类推
    # round[ random.ranint(0, length(round)) ] 即可按照概率随机选出一个兵种

    @classmethod
    def init(cls):
        for u in CONFIG.UNIT.values():
            if u.race in cls.UNIT:
                cls.UNIT[u.race].append(u)
            else:
                cls.UNIT[u.race] = [u]

        for race_id, units in cls.UNIT.iteritems():
            round_one = []
            round_two = []
            round_three = []

            for u in units:
                round_one.extend( [u.id] * u.first_trig )
                round_two.extend( [u.id] * u.second_trig )
                round_three.extend( [u.id] * u.third_trig )

            cls.UNIT[race_id] = [round_one, round_two, round_three]


    @classmethod
    def get(cls, race, round_index):
        # 根据种族和第几回合来随机选择兵种
        units = cls.UNIT[race][round_index-1]
        index = random.randint(0, len(units))
        return units[index]


Unit.init()



class BattleStaff(object):
    # 比赛中的队员
    def __init__(self, char_id, staff_id, round_index, winning_rate):
        self.id = staff_id
        self.winning_rate = winning_rate

        self.staff = Staff.new(char_id, staff_id)

        self.unit_id = Unit.get(self.staff.race, round_index)

    def battle(self, other):
        # TODO real battle
        y = random.randint(-20, 20)
        self.winning_rate += y
        other.winning_rate -= y



class Battle(object):
    def __init__(self, char_id, staff_one_id, staff_two_id):
        self.char_id = char_id
        self.staff_one_id = staff_one_id
        self.staff_two_id = staff_two_id
        self.round_index = 1

        self.winning_staff_id = 0


    def battle(self):
        staff_one_winning_rate = 50
        staff_two_winning_rate = 50
        for i in range(1, 4):
            staff_one = BattleStaff(self.char_id, self.staff_one_id, i, staff_one_winning_rate)
            staff_two = BattleStaff(self.char_id, self.staff_two_id, i, staff_two_winning_rate)

            staff_one.battle(staff_two)

            staff_one_winning_rate = staff_one.winning_rate
            staff_two_winning_rate = staff_two.winning_rate

            if staff_one_winning_rate >= 90:
                self.winning_staff_id = self.staff_one_id
                break

            if staff_two_winning_rate >= 90:
                self.winning_staff_id = self.staff_two_id
                break

        if self.winning_staff_id:
            return

        if staff_one_winning_rate == staff_two_winning_rate:
            self.winning_staff_id = random.choice([self.staff_one_id, self.staff_two_id])

        elif staff_one_winning_rate > staff_two_winning_rate:
            rate = (staff_two_winning_rate * 1.0 / 100) ** 2 * 100
            if random.randint(0, 100) <= rate:
                self.winning_staff_id = self.staff_two_id
            else:
                self.winning_staff_id = self.staff_one_id

        else:
            rate = (staff_one_winning_rate * 1.0 / 100) ** 2 * 100
            if random.randint(0, 100) <= rate:
                self.winning_staff_id = self.staff_one_id
            else:
                self.winning_staff_id = self.staff_two_id




