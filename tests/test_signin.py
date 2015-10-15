# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_signin
Date Created:   2015-09-21 17:28
Description:

"""

import arrow
from django.conf import settings
from core.mongo import MongoSignIn
from core.activity.signin import SignIn


class TestSignIn(object):
    def teardown(self):
        MongoSignIn.db(1).drop()

    def test_send_notify(self):
        SignIn(1, 1).send_notify()

    def test_sign(self):
        SignIn(1, 1).sign(1)
        doc = MongoSignIn.db(1).find_one({'_id': 1})

        info = doc['sign']['1']
        assert len(info) == 1
        assert arrow.get(info[0], 'YYYY-MM-DD HH:mm:ss').to(settings.TIME_ZONE).date() == \
               arrow.utcnow().to(settings.TIME_ZONE).date()
