# -*- coding: utf-8 -*-
"""
Author:         Ouyang_Yibei <said047@163.com>
Filename:       test_match
Date Created:   2015-11-17 19:18
Description:

"""
import random

from config.staff import ConfigStaff
from config.unit import ConfigUnit

from core.match import Match


def get_random_staffs(num):
    return random.sample(ConfigStaff.INSTANCES.keys(), num)


def get_random_policy():
    return random.choice(ConfigUnit.INSTANCES.keys())


class TestMatch(object):
    def __init__(self):
        self.staffs_one = get_random_staffs(5)
        self.staffs_two = get_random_staffs(5)
        self.policy_one = get_random_policy()
        self.policy_two = get_random_policy()
