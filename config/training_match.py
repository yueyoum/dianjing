# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training_match
Date Created:   2015-12-08 16:17
Description:

"""

from config.base import ConfigBase

class TrainingMatchReward(object):
    __slots__ = ['id', 'reward', 'additional_reward']
    def __init__(self):
        self.id = 0
        self.reward = 0
        self.additional_reward = 0


class ConfigTrainingMatchReward(ConfigBase):
    EntityClass = TrainingMatchReward
    INSTANCES = {}
    FILTER_CACHE = {}
    
    @classmethod
    def get(cls, _id):
        """

        :rtype : TrainingMatchReward
        """
        return super(ConfigTrainingMatchReward, cls).get(_id)
