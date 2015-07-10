# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       base
Date Created:   2015-07-09 23:28
Description:

"""

import json

class ConfigBase(object):
    EntityClass = None

    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def initialize(cls, fixture):
        for f in fixture:
            s = cls.EntityClass()
            s.id = f['pk']
            for k, v in f['fields'].iteritems():
                if k not in cls.EntityClass.__slots__:
                    continue

                setattr(s, k, v)

            cls.INSTANCES[s.id] = s

    @classmethod
    def get(cls, id):
        return cls.INSTANCES[id]


    @classmethod
    def filter(cls, **condition):
        """

        :rtype : dict
        """
        cache_key = json.dumps(condition)
        if cache_key not in cls.FILTER_CACHE:
            result = {}

            for k, v in cls.INSTANCES.iteritems():
                if cls._do_filter(v, **condition):
                    result[k] = v

            cls.FILTER_CACHE[cache_key] = result

        return cls.FILTER_CACHE[cache_key]


    @classmethod
    def _do_filter(cls, obj, **condition):
        for k, v in condition.iteritems():
            if getattr(obj, k) != v:
                return False
            return True
