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
from core.signin import get_sign_day, SignIn


class TestGetSignDay(object):
    def test_get_sign_day_a(self):
        sign_days = [1, 2, 3, 4, 5, 6, 7]
        sign_test_divisor = 1
        sign_test_value = 0

        assert get_sign_day(1, sign_days, sign_test_divisor) == 1
        assert get_sign_day(2, sign_days, sign_test_divisor) == 2
        assert get_sign_day(3, sign_days, sign_test_divisor) == 3
        assert get_sign_day(4, sign_days, sign_test_divisor) == 4
        assert get_sign_day(5, sign_days, sign_test_divisor) == 5
        assert get_sign_day(6, sign_days, sign_test_divisor) == 6
        assert get_sign_day(7, sign_days, sign_test_divisor) == 7

        assert get_sign_day(8, sign_days, sign_test_divisor) == 1
        assert get_sign_day(9, sign_days, sign_test_divisor) == 2
        assert get_sign_day(10, sign_days, sign_test_divisor) == 3
        assert get_sign_day(11, sign_days, sign_test_divisor) == 4
        assert get_sign_day(12, sign_days, sign_test_divisor) == 5
        assert get_sign_day(13, sign_days, sign_test_divisor) == 6
        assert get_sign_day(14, sign_days, sign_test_divisor) == 7

        assert get_sign_day(15, sign_days, sign_test_divisor) == 1
        assert get_sign_day(150, sign_days, sign_test_divisor) == 3

    def test_get_sign_day_b(self):
        sign_days = range(1, 31)
        sign_test_divisor = 1
        sign_test_value = 0

        assert get_sign_day(1, sign_days, sign_test_divisor) == 1
        assert get_sign_day(2, sign_days, sign_test_divisor) == 2
        assert get_sign_day(3, sign_days, sign_test_divisor) == 3
        assert get_sign_day(4, sign_days, sign_test_divisor) == 4
        assert get_sign_day(5, sign_days, sign_test_divisor) == 5
        assert get_sign_day(6, sign_days, sign_test_divisor) == 6
        assert get_sign_day(30, sign_days, sign_test_divisor) == 30

        assert get_sign_day(31, sign_days, sign_test_divisor) == 1
        assert get_sign_day(32, sign_days, sign_test_divisor) == 2
        assert get_sign_day(33, sign_days, sign_test_divisor) == 3
        assert get_sign_day(34, sign_days, sign_test_divisor) == 4
        assert get_sign_day(35, sign_days, sign_test_divisor) == 5
        assert get_sign_day(36, sign_days, sign_test_divisor) == 6
        assert get_sign_day(60, sign_days, sign_test_divisor) == 30

        assert get_sign_day(91, sign_days, sign_test_divisor) == 1
        assert get_sign_day(160, sign_days, sign_test_divisor) == 10

    def test_get_sign_day_c(self):
        sign_days = [1, 3, 5, 7, 9]
        sign_test_divisor = 2
        sign_test_value = 1

        assert get_sign_day(1, sign_days, sign_test_divisor) == 1
        assert get_sign_day(3, sign_days, sign_test_divisor) == 3
        assert get_sign_day(5, sign_days, sign_test_divisor) == 5
        assert get_sign_day(7, sign_days, sign_test_divisor) == 7
        assert get_sign_day(9, sign_days, sign_test_divisor) == 9

        assert get_sign_day(11, sign_days, sign_test_divisor) == 1
        assert get_sign_day(13, sign_days, sign_test_divisor) == 3
        assert get_sign_day(15, sign_days, sign_test_divisor) == 5
        assert get_sign_day(17, sign_days, sign_test_divisor) == 7
        assert get_sign_day(19, sign_days, sign_test_divisor) == 9

        assert get_sign_day(21, sign_days, sign_test_divisor) == 1
        assert get_sign_day(23, sign_days, sign_test_divisor) == 3
        assert get_sign_day(25, sign_days, sign_test_divisor) == 5
        assert get_sign_day(27, sign_days, sign_test_divisor) == 7
        assert get_sign_day(29, sign_days, sign_test_divisor) == 9

        assert get_sign_day(31, sign_days, sign_test_divisor) == 1

    def test_get_sign_day_d(self):
        sign_days = [1, 3, 5, 7, 9, 11, 13]
        sign_test_divisor = 2
        sign_test_value = 1

        assert get_sign_day(1, sign_days, sign_test_divisor) == 1
        assert get_sign_day(3, sign_days, sign_test_divisor) == 3
        assert get_sign_day(5, sign_days, sign_test_divisor) == 5
        assert get_sign_day(7, sign_days, sign_test_divisor) == 7
        assert get_sign_day(9, sign_days, sign_test_divisor) == 9
        assert get_sign_day(11, sign_days, sign_test_divisor) == 11
        assert get_sign_day(13, sign_days, sign_test_divisor) == 13

        assert get_sign_day(15, sign_days, sign_test_divisor) == 1
        assert get_sign_day(17, sign_days, sign_test_divisor) == 3
        assert get_sign_day(19, sign_days, sign_test_divisor) == 5
        assert get_sign_day(21, sign_days, sign_test_divisor) == 7
        assert get_sign_day(23, sign_days, sign_test_divisor) == 9
        assert get_sign_day(25, sign_days, sign_test_divisor) == 11
        assert get_sign_day(27, sign_days, sign_test_divisor) == 13

        assert get_sign_day(29, sign_days, sign_test_divisor) == 1
        assert get_sign_day(31, sign_days, sign_test_divisor) == 3

    def test_get_sign_day_e(self):
        sign_days = [2, 4, 6, 8, 10]
        sign_test_divisor = 2
        sign_test_value = 0

        assert get_sign_day(2, sign_days, sign_test_divisor) == 2
        assert get_sign_day(4, sign_days, sign_test_divisor) == 4
        assert get_sign_day(6, sign_days, sign_test_divisor) == 6
        assert get_sign_day(8, sign_days, sign_test_divisor) == 8
        assert get_sign_day(10, sign_days, sign_test_divisor) == 10

        assert get_sign_day(12, sign_days, sign_test_divisor) == 2
        assert get_sign_day(14, sign_days, sign_test_divisor) == 4
        assert get_sign_day(16, sign_days, sign_test_divisor) == 6
        assert get_sign_day(18, sign_days, sign_test_divisor) == 8
        assert get_sign_day(20, sign_days, sign_test_divisor) == 10

        assert get_sign_day(22, sign_days, sign_test_divisor) == 2

    def test_get_sign_day_f(self):
        sign_days = [2, 4, 6]
        sign_test_divisor = 2
        sign_test_value = 0

        assert get_sign_day(2, sign_days, sign_test_divisor) == 2
        assert get_sign_day(4, sign_days, sign_test_divisor) == 4
        assert get_sign_day(6, sign_days, sign_test_divisor) == 6

        assert get_sign_day(8, sign_days, sign_test_divisor) == 2
        assert get_sign_day(10, sign_days, sign_test_divisor) == 4
        assert get_sign_day(12, sign_days, sign_test_divisor) == 6

        assert get_sign_day(14, sign_days, sign_test_divisor) == 2
        assert get_sign_day(16, sign_days, sign_test_divisor) == 4

    def test_get_sign_day_g(self):
        sign_days = [5, 8, 11, 14, 17]
        sign_test_divisor = 3
        sign_test_value = 2

        assert get_sign_day(5, sign_days, sign_test_divisor) == 5
        assert get_sign_day(8, sign_days, sign_test_divisor) == 8
        assert get_sign_day(11, sign_days, sign_test_divisor) == 11
        assert get_sign_day(14, sign_days, sign_test_divisor) == 14
        assert get_sign_day(17, sign_days, sign_test_divisor) == 17

        assert get_sign_day(20, sign_days, sign_test_divisor) == 5
        assert get_sign_day(23, sign_days, sign_test_divisor) == 8
        assert get_sign_day(26, sign_days, sign_test_divisor) == 11
        assert get_sign_day(29, sign_days, sign_test_divisor) == 14
        assert get_sign_day(32, sign_days, sign_test_divisor) == 17

        assert get_sign_day(35, sign_days, sign_test_divisor) == 5
        assert get_sign_day(38, sign_days, sign_test_divisor) == 8
        assert get_sign_day(41, sign_days, sign_test_divisor) == 11
        assert get_sign_day(44, sign_days, sign_test_divisor) == 14
        assert get_sign_day(47, sign_days, sign_test_divisor) == 17

        assert get_sign_day(50, sign_days, sign_test_divisor) == 5
        assert get_sign_day(53, sign_days, sign_test_divisor) == 8

    def test_get_sign_day_h(self):
        sign_days = [20, 31, 42, 53]
        sign_test_divisor = 11
        sign_test_value = 9

        assert get_sign_day(20, sign_days, sign_test_divisor) == 20
        assert get_sign_day(31, sign_days, sign_test_divisor) == 31
        assert get_sign_day(42, sign_days, sign_test_divisor) == 42
        assert get_sign_day(53, sign_days, sign_test_divisor) == 53

        assert get_sign_day(64, sign_days, sign_test_divisor) == 20
        assert get_sign_day(75, sign_days, sign_test_divisor) == 31
        assert get_sign_day(86, sign_days, sign_test_divisor) == 42
        assert get_sign_day(97, sign_days, sign_test_divisor) == 53

        assert get_sign_day(108, sign_days, sign_test_divisor) == 20
        assert get_sign_day(119, sign_days, sign_test_divisor) == 31
        assert get_sign_day(130, sign_days, sign_test_divisor) == 42
        assert get_sign_day(141, sign_days, sign_test_divisor) == 53

        assert get_sign_day(152, sign_days, sign_test_divisor) == 20
        assert get_sign_day(163, sign_days, sign_test_divisor) == 31

    def test_get_sign_day_i(self):
        sign_days = [1]
        sign_test_divisor = 1
        sign_test_value = 0

        assert get_sign_day(1, sign_days, sign_test_divisor) == 1
        assert get_sign_day(2, sign_days, sign_test_divisor) == 1
        assert get_sign_day(3, sign_days, sign_test_divisor) == 1
        assert get_sign_day(4, sign_days, sign_test_divisor) == 1

        assert get_sign_day(152, sign_days, sign_test_divisor) == 1
        assert get_sign_day(163, sign_days, sign_test_divisor) == 1


class TestSignIn(object):
    def teardown(self):
        MongoSignIn.db(1).drop()

    def test_send_notify(self):
        SignIn(1, 1).send_notify()

    def test_sign(self):
        SignIn(1, 1).sign(1)
        doc = MongoSignIn.db(1).find_one({'_id': 1})

        info = doc['sign']['1']
        assert info['last_sign_at'] == arrow.utcnow().to(settings.TIME_ZONE).format("YYYY-MM-DD")
        assert info['last_sign_day'] == 1
        assert info['is_continued'] == True
