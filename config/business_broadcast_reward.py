# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       business_broadcast_reward
Date Created:   2015-12-24 11:07
Description:

"""

import random

from config.base import ConfigBase


class BusinessBroadCastReward(object):
    __slots__ = ['id', 'amount', 'prob']

    def __init__(self):
        self.id = 0
        self.amount = 0
        self.prob = 0


def _get_reward(prob):
    if random.randint(1, 100) <= prob:
        return None

    values = ConfigBusinessBroadCastReward.VALUES
    """:type: list[BusinessBroadCastReward]"""

    prob = random.randint(1, ConfigBusinessBroadCastReward.MAX_PROB_VALUE)
    for v in values:
        if v.prob >= prob:
            return [v.id, v.amount]

    return None


class ConfigBusinessBroadCastReward(ConfigBase):
    EntityClass = BusinessBroadCastReward
    INSTANCES = {}
    FILTER_CACHE = {}

    VALUES = []
    MAX_PROB_VALUE = 0

    REWARD_INTERVAL_SECONDS = 60

    @classmethod
    def initialize(cls, fixture):
        super(ConfigBusinessBroadCastReward, cls).initialize(fixture)
        cls.VALUES = cls.INSTANCES.values()
        for i in range(1, len(cls.VALUES)):
            cls.VALUES[i].prob += cls.VALUES[i - 1].prob

        cls.MAX_PROB_VALUE = cls.VALUES[-1].prob

    @classmethod
    def get_rewards(cls, prob_list):
        """

        :type prob_list: list[int]
        """
        rewards = {}
        for prob in prob_list:
            got = _get_reward(prob)
            if not got:
                continue

            if got[0] in rewards:
                rewards[got[0]] += got[1]
            else:
                rewards[got[0]] = got[1]

        return rewards.items()
