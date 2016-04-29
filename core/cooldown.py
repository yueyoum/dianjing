# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       cooldown
Date Created:   2016-04-29 15-54
Description:

"""

from core.db import RedisDB

class CD(object):
    __slots__ = ['server_id', 'char_id']
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def make_key(self):
        raise NotImplementedError()

    def set(self, cd_seconds):
        key = self.make_key()

        result = RedisDB.get().set(key, 1, ex=cd_seconds, nx=True)
        if not result:
            #是设置失败，cd还没有消失
            return False

        return True

    def get_cd_seconds(self):
        ttl = RedisDB.get().ttl(self.make_key())
        if not ttl:
            return 0
        return ttl


# 竞技场刷新CD
class ArenaRefreshCD(CD):
    __slots__ = []

    def make_key(self):
        return 'cd:arena_refresh:{0}:{1}'.format(self.server_id, self.char_id)

# 竞技场主动挑战CD
class ArenaMatchCD(CD):
    __slots__ = []

    def make_key(self):
        return 'cd:arena_match:{0}:{1}'.format(self.server_id, self.char_id)
