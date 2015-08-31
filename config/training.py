# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       training
Date Created:   2015-07-21 00:15
Description:

"""

import random

from config.base import ConfigBase

class Training(object):
    __slots__ = [
        'id', 'on_sell', 'need_building_level', 'tp',
        'cost_type', 'cost_value', 'minutes',
        'package',
        'skill_id', 'skill_level',
    ]
    
    def __init__(self):
        self.id = 0
        self.on_sell = 0
        self.need_building_level = 0
        self.tp = 0
        self.cost_type = 0
        self.cost_value = 0
        self.minutes = 0
        self.package = 0
        self.skill_id = 0
        self.skill_level = 0


class ConfigTraining(ConfigBase):
    EntityClass = Training
    INSTANCES = {}
    FILTER_CACHE = {}
    
    @classmethod
    def get(cls, id):
        """

        :rtype : Training
        """
        return super(ConfigTraining, cls).get(id)


    @classmethod
    def refreshed_ids(cls, level, amount):
        if level == 1:
            trainings = cls.filter(need_building_level=1, on_sell=True)
            return random.sample(trainings.keys(), amount)

        ids = []

        # 保证当前等级有一个
        # 然后从小于当前等级的训练中取其他的，
        # 但是也要保证每个等级至少有一个
        trainings = cls.filter(need_building_level=level, on_sell=True)
        ids.append(random.choice(trainings.keys()))

        level -= 1
        training_ids = []

        while level >= 1:
            this_level_trainings = cls.filter(need_building_level=level, on_sell=True)
            this_level_ids = this_level_trainings.keys()
            this_id = random.choice(this_level_ids)

            ids.append(this_id)

            this_level_ids.remove(this_id)
            training_ids.extend(this_level_ids)

            level -= 1

        need_additional_amount = amount - len(ids)
        ids.extend(random.sample(training_ids, need_additional_amount))

        return ids



