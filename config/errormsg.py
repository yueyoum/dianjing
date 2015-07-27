# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       errormsg
Date Created:   2015-07-27 14:53
Description:

"""

from config.base import ConfigBase

class ErrorMessage(object):
    __slots__ = ['id', 'error_index']

    def __init__(self):
        self.id = 0
        self.error_index = ""


class ConfigErrorMessage(ConfigBase):
    EntityClass = ErrorMessage
    INSTANCES = {}
    FILTER_CACHE = {}

    INSTANCES_REVERSE = {}

    @classmethod
    def initialize(cls, fixture):
        super(ConfigErrorMessage, cls).initialize(fixture)
        cls.INSTANCES_REVERSE = {v.error_index: k for k, v in cls.INSTANCES.iteritems()}


    @classmethod
    def get(cls, id):
        """

        :rtype : ErrorMessage
        """
        return super(ConfigErrorMessage, cls).get(id)


    @classmethod
    def get_error_id(cls, error_index):
        return cls.INSTANCES_REVERSE[error_index]
