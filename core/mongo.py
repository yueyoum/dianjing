# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       mongo
Date Created:   2015-07-08 02:13
Description:

"""

class Null(object):
    pass

null = Null()

DEFAULT_COMMON_DOCUMENT = {
    '_id': null,
    'value': null,
}

DEFAULT_CHARACTER_DOCUMENT = {
    '_id': null,
    'name': null,

    'club': {
        'name': null,
        'flag': null,
        'level': 1,
        'renown': 0,
        'vip': 0,
        'exp': 0,
        'gold': 0,
        'diamond': 0,
    },

    'staffs': {}
}

DEFAULT_RECRUIT_DOCUMENT = {
    '_id': null,
    'tp': null,
    'staffs': [],
    'times': {}
}


class Document(object):
    DOCUMENTS = {
        "common": DEFAULT_COMMON_DOCUMENT,
        "character": DEFAULT_CHARACTER_DOCUMENT,
        "recruit": DEFAULT_RECRUIT_DOCUMENT,
    }

    @classmethod
    def get(cls, name):
        return cls.DOCUMENTS[name].copy()

