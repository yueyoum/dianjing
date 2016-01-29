# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training_match
Date Created:   2015-12-08 16:17
Description:

"""

from config.base import ConfigBase

class TrainingMatchReward(object):
    __slots__ = ['id', 'reward', 'score']
    def __init__(self):
        self.id = 0
        self.reward = 0
        self.score = 0


class TrainingMatchStore(object):
    __slots__ = ['id', 'times_limit', 'score', 'item', 'item_amount']
    def __init__(self):
        self.id = 0
        self.times_limit = 0
        self.score = 0
        self.item = 0
        self.item_amount = 0


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


class ConfigTrainingMatchStore(ConfigBase):
    EntityClass = TrainingMatchStore
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype : TrainingMatchStore
        """
        return super(ConfigTrainingMatchStore, cls).get(_id)
