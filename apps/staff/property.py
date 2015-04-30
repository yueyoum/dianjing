# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       property
Date Created:   2015-04-30 10:42
Description:

"""

import json

class StaffProperty(object):
    PROPERTY = (
        ("jingong", "jg"),
        ("qianzhi", "qz"),
        ("xintai", "xt"),
        ("baobing", "bb"),
        ("fangshou", "fs"),
        ("yunying", "yy"),
        ("yishi", "ys"),
        ("caozuo", "cz"),
    )

    NAME_DICT = {k: v for k, v in PROPERTY}
    SHORT_NAME_DICT = {v: k for k, v in PROPERTY}

    # this is used for Staff models.
    DEFAULT_PROPERTY_ADD = json.dumps( {v: 0 for k, v in PROPERTY} )

    @classmethod
    def name_to_short_name(cls, name):
        return cls.NAME_DICT[name]

    @classmethod
    def short_name_to_name(cls, short_name):
        return cls.SHORT_NAME_DICT[short_name]
