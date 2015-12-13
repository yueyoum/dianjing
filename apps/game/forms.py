# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       forms
Date Created:   2015-12-12 19:55
Description:

"""

from django import forms
from duckadmin import DuckForm

from core.mongo import MongoCharacter

def make_data(doc):
    club = doc['club']
    club['match_staffs'] = ','.join([str(i) for i in club['match_staffs']])
    club['tibu_staffs'] = ','.join([str(i) for i in club['tibu_staffs']])
    return club

class MyForm(DuckForm):
    app_label = 'game'
    model_name = 'club'
    verbose_name = '俱乐部'
    pk_name = 'id'

    id = forms.IntegerField()
    name = forms.CharField()
    level = forms.IntegerField()
    renown = forms.IntegerField()
    vip = forms.IntegerField()
    gold = forms.IntegerField()
    diamond = forms.IntegerField()
    policy = forms.IntegerField()
    match_staffs = forms.CharField()
    tibu_staffs = forms.CharField()

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
        pk = data.pop('id')

        match_staffs = [int(i) for i in data['match_staffs'].split(',')]
        tibu_staffs = [int(i) for i in data['tibu_staffs'].split(',')]

        data['match_staffs'] = match_staffs
        data['tibu_staffs'] = tibu_staffs

        MongoCharacter.db(1).update_one(
            {'_id': pk},
            {'$set': {'club': data}}
        )
