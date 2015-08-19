# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_lock
Date Created:   2015-08-13 19:24
Description:

"""

import threading

from core.db import MongoDB
from core.lock import LadderLock

class TestLock(object):
    def setup(self):
        MongoDB.get(1).test_counter.insert_one({'_id':1, 'value': 0})

    def teardown(self):
        MongoDB.get(1).test_counter.drop()


    def get_counter_value(self):
        return MongoDB.get(1).test_counter.find_one({'_id': 1})['value']

    def incr_counter(self):
        value = self.get_counter_value()
        MongoDB.get(1).test_counter.update_one({'_id': 1}, {'$set': {'value': value+1}})


    def test_simple_case(self):
        with LadderLock(1).lock():
            self.incr_counter()

        assert self.get_counter_value() == 1


    def test_concurrency(self):
        def worker():
            with LadderLock(1).lock():
                self.incr_counter()

        amount = 100

        threads = []
        for i in range(amount):
            t = threading.Thread(target=worker)
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        value = self.get_counter_value()
        assert value == amount
