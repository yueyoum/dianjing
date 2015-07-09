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
    }
}


class Document(object):
    DOCUMENTS = {
        "character": DEFAULT_CHARACTER_DOCUMENT
    }

    @classmethod
    def get(cls, name):
        return cls.DOCUMENTS[name].copy()

