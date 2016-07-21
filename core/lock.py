# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       lock
Date Created:   2015-08-13 18:20
Description:

"""

import time

from contextlib import contextmanager
from core.db import RedisDB

def remove_lock_key(key):
    RedisDB.get().delete(key)


class LockTimeOut(Exception):
    pass


class RedisLock(object):
    __slots__ = ['server_id', 'char_id', 'key']

    INTERVAL = 0.1

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.key = self.make_key()

    def make_key(self):
        raise NotImplementedError()

    @contextmanager
    def lock(self, wait_timeout=5, hold_seconds=5):
        """

        :param wait_timeout: 等待获取锁的超时时间，超过这个时间没有获取到锁，将抛出LockTimeOut异常
        :param hold_seconds: 获取到锁以后，要保持的最长时间。
                             程序在可以在这个时间点前可以主动放弃锁。
                             如果超过hold_seconds后，还没有主动放弃，那么锁将自动释放
                             以此来应对程序获得锁以后出错没有主动释放形成死锁的问题
        """

        t = 0
        while True:
            if t > wait_timeout:
                raise LockTimeOut()

            result = RedisDB.get().set(self.key, 1, ex=hold_seconds, nx=True)
            if result:
                # got the lock
                break

            time.sleep(self.INTERVAL)
            t += self.INTERVAL

        try:
            yield self
        finally:
            RedisDB.get().delete(self.key)

    def release(self):
        RedisDB.get().delete(self.key)


# 锁住整个竞技场
class ArenaLock(RedisLock):
    def make_key(self):
        return 'lock:arena:{0}'.format(self.server_id)
