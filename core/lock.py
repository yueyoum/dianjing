# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       lock
Date Created:   2015-08-13 18:20
Description:

"""

import time

from contextlib import contextmanager

from pymongo.errors import DuplicateKeyError
from core.db import MongoDB

class LockTimeOut(Exception):
    pass


class Lock(object):
    KEY = None
    def __init__(self, server_id):
        self.server_id = server_id
        self.mongo = MongoDB.get(server_id)


    @contextmanager
    def lock(self, timeout=5):
        t = 0
        while True:
            if t > timeout:
                raise LockTimeOut()

            try:
                self.mongo.lock.insert_one({'_id': self.KEY})
            except DuplicateKeyError:
                time.sleep(0.1)
                t += 0.1
            else:
                break

        try:
            yield
        finally:
            self.mongo.lock.delete_one({'_id': self.KEY})


class LadderNPCLock(Lock):
    KEY = 'ladder_npc'

class LadderLock(Lock):
    KEY = 'ladder'
