# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       test_match
Date Created:   2015-11-17 19:18
Description:

"""
import random
import time

from config.staff import ConfigStaff
from config.unit import ConfigPolicy
from config.challenge import ConfigChallengeMatch

from core.match import Match, ClubMatch
from core.abstract import AbstractStaff
from core.challenge import ChallengeNPCClub


def get_random_staffs(num):
    return random.sample(ConfigStaff.INSTANCES.keys(), num)


def get_random_policy():
    return random.choice(ConfigPolicy.INSTANCES.keys())


def get_abstract_staff():
    staff = AbstractStaff()
    staff_config = ConfigStaff.get(random.choice(ConfigStaff.INSTANCES.keys()))

    staff.server_id = 1
    staff.char_id = 1
    staff.id = staff_config.id
    staff.race = staff_config.race
    staff.level = random.randint(1, 10)
    staff.exp = random.randint(1, 100)
    staff.status = random.randint(1, 7)
    staff.quality = 0
    staff.jingong = staff_config.jingong * random.randint(1, 8)
    staff.qianzhi = staff_config.qianzhi * random.randint(1, 8)
    staff.xintai = staff_config.xintai * random.randint(1, 8)
    staff.baobing = staff_config.baobing * random.randint(1, 8)
    staff.fangshou = staff_config.fangshou * random.randint(1, 8)
    staff.yunying = staff_config.yunying * random.randint(1, 8)
    staff.yishi = staff_config.yishi * random.randint(1, 8)
    staff.caozuo = staff_config.caozuo * random.randint(1, 8)
    staff.zhimingdu = random.randint(1, 100)

    return staff, get_random_policy()


class TestMatch(object):
    def reset(self):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_round(self):
        staffs_one, policy_one = get_abstract_staff()
        staffs_two, policy_two = get_abstract_staff()

        start = time.clock()
        for i in range(1, 3 * 1000 * 100):
            msg = Match(staffs_one, staffs_two, policy_one, policy_two).round()
            # assert msg
        print time.clock() - start

    def test_start(self):
        staffs_one, policy_one = get_abstract_staff()
        staffs_two, policy_two = get_abstract_staff()
        start = time.clock()
        for i in range(1, 100 * 1000 + 1):
            msg = Match(staffs_one, staffs_one, policy_one, policy_one).start()
            assert msg
            # print msg

        print time.clock() - start


class TestClubMatch(object):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_start(self):
        config = ConfigChallengeMatch.get(random.choice(ConfigChallengeMatch.INSTANCES.keys()))

        club_one = ChallengeNPCClub(config.id)
        club_two = ChallengeNPCClub(config.id)

        start = time.time()
        for i in range(1, 2000 + 1):
            msg = ClubMatch(club_one, club_two).start()
            assert msg

        print time.time() - start



