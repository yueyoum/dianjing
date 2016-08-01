# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       forms
Date Created:   2015-12-12 19:55
Description:

"""

from django import forms
from duckadmin import DuckForm

from core.mongo import MongoOperationLog


class IterWrapper(object):
    __slots__ = ['docs', 'count']
    def __init__(self, docs):
        self.docs = docs
        self.count = docs.count()

    def __iter__(self):
        for doc in self.docs:
            yield doc

    def __len__(self):
        return self.count

class FormOperationLog(DuckForm):
    app_label = 'game'
    model_name = 'operation_log'
    verbose_name = u'操作日志'
    pk_name = 'id'

    _id = forms.CharField()
    char_id = forms.IntegerField()
    action = forms.CharField()
    ret = forms.IntegerField()
    timestamp = forms.IntegerField()
    cost_millisecond = forms.IntegerField()

    @classmethod
    def get_params(cls, request):
        sid = request.GET.get('sid', 0)

        char_id = request.GET.get('char_id', None)
        if char_id:
            char_id = int(char_id)

        order = request.GET.get('order', '')

        return {
            'sid': int(sid),
            'char_id': char_id,
            'order': order,
        }

    @classmethod
    def get_count(cls, request):
        params = cls.get_params(request)

        if not params['sid']:
            return 0

        if params['char_id']:
            condition = {'char_id': params['char_id']}
        else:
            condition = {}

        return MongoOperationLog.db(params['sid']).find(condition).count()

    @classmethod
    def get_data(cls, request, start=None, stop=None):
        params = cls.get_params(request)
        if not params['sid']:
            return []

        if params['char_id']:
            condition = {'char_id': params['char_id']}
        else:
            condition = {}

        docs = MongoOperationLog.db(params['sid']).find(condition)

        if params['order']:
            if params['order'].startswith('-'):
                docs.sort(params['order'][1:], -1)
            else:
                docs.sort(params['order'])

        if start or stop:
            docs.skip(start).limit(stop - start)

        return IterWrapper(docs)

    @classmethod
    def get_data_by_pk(cls, request, pk):
        params = cls.get_params(request)
        if not params['sid']:
            raise cls.DoesNotExist()

        doc = MongoOperationLog.db(1).find_one({'_id': pk})

        if doc:
            return doc

        raise cls.DoesNotExist()

    @classmethod
    def create_data(cls, request, data):
        raise RuntimeError("can not create")

    @classmethod
    def update_data(cls, request, data):
        raise RuntimeError("can not create")
