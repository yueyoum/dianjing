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
from core.db import MongoDB, RedisDB


class LockTimeOut(Exception):
    pass


class RedisLock(object):
    INTERVAL = 0.1
    KEY = None

    def __init__(self, server_id):
        self.server_id = server_id

    @contextmanager
    def lock(self, timeout=5, lock_seconds=10, key=None):
        key = "{0}:{1}".format(key or self.KEY, self.server_id)

        t = 0
        while True:
            if t > timeout:
                raise LockTimeOut()

            result = RedisDB.get().set(key, 1, ex=lock_seconds, nx=True)
            if result:
                # got the lock
                break

            time.sleep(self.INTERVAL)
            t += self.INTERVAL

        try:
            yield
        finally:
            RedisDB.get().delete(key)


class MongoLock(object):
    INTERVAL = 0.1
    KEY = None

    def __init__(self, server_id):
        self.server_id = server_id
        self.mongo = MongoDB.get(server_id)

    @contextmanager
    def lock(self, timeout=5, key=None):
        if not key:
            key = self.KEY

        t = 0
        while True:
            if t > timeout:
                raise LockTimeOut()

            try:
                self.mongo.lock.insert_one({'_id': key})
            except DuplicateKeyError:
                time.sleep(self.INTERVAL)
                t += self.INTERVAL
            else:
                break

        try:
            yield
        finally:
            self.mongo.lock.delete_one({'_id': key})


Lock = RedisLock


class LadderNPCLock(Lock):
    KEY = 'lock_ladder_npc'


class LadderLock(Lock):
    KEY = 'lock_ladder'


class LadderStoreLock(Lock):
    KEY = 'lock_ladder_store'
