# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       collection
Date Created:   2016-05-27 15-09
Description:

"""


from config.base import ConfigBase

class Collection(object):
    __slots__ = ['id', 'talent_effect_id']
    def __init__(self):
        self.id = 0
        self.talent_effect_id = 0


class ConfigCollection(ConfigBase):
    EntityClass = Collection
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: Collection
        """
        return super(ConfigCollection, cls).get(_id)
