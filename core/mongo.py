# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       mongo
Date Created:   2015-07-08 02:13
Description:

"""

from core.db import get_mongo_db

class Field(object):
    pass

class ValueField(Field):
    pass

class ListField(Field):
    pass

class DictField(Field):
    pass

class Document(object):
    class Meta:
        collection_name = None
        index = []
        unique = []

