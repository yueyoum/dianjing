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

class FormOperationLog(DuckForm):
    app_label = 'game'
    model_name = 'operation_log'
    verbose_name = '操作日志'
    pk_name = 'id'

    _id = forms.CharField()
    char_id = forms.IntegerField()
    action = forms.CharField()
    ret = forms.IntegerField()
    timestamp = forms.IntegerField()
    cost_millisecond = forms.IntegerField()

    @classmethod
    def get_data(cls):
        # TODO servers ?
        docs = MongoCharacter.db(1).find().sort('last_login', -1).limit(100)
        return (make_data(d) for d in docs)

    @classmethod
    def get_data_by_pk(cls, pk):
        pk = int(pk)
        doc = MongoCharacter.db(1).find_one(
            {'_id': pk},
            {'club': 1}
        )

        if doc:
            return make_data(doc)

        raise cls.DoesNotExist()

    @classmethod
    def create_data(cls, data):
        raise RuntimeError("can not create")

    @classmethod
    def update_data(cls, data):
        raise RuntimeError("can not create")
