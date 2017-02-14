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
            # 是设置失败，cd还没有消失
            return False

        return True

    def get_cd_seconds(self):
        ttl = RedisDB.get().ttl(self.make_key())
        if not ttl:
            return 0
        return ttl

    def clean(self):
        RedisDB.get().delete(self.make_key())


# 竞技场刷新CD
class ArenaRefreshCD(CD):
    __slots__ = []

    def make_key(self):
        return 'cd:arena_refresh:{0}:{1}'.format(self.server_id, self.char_id)


# 竞技场挑战CD
# 不会暴露给客户端，只是服务器内部使用的
class ArenaMatchCD(CD):
    __slots__ = ['rival_id']

    def __init__(self, server_id, char_id, rival_id):
        super(ArenaMatchCD, self).__init__(server_id, char_id)
        self.rival_id = rival_id

    def make_key(self):
        return 'cd:arena_match:{0}:{1}:{2}'.format(self.server_id, self.char_id, self.rival_id)


# 掠夺搜索CD
class PlunderSearchCD(CD):
    __slots__ = []

    def make_key(self):
        return 'cd:plunder_search:{0}:{1}'.format(self.server_id, self.char_id)


# 掠夺挑战CD
class PlunderMatchCD(CD):
    __slots__ = ['rival_id']

    def __init__(self, server_id, char_id, rival_id):
        super(PlunderMatchCD, self).__init__(server_id, char_id)
        self.rival_id = rival_id

    def make_key(self):
        return 'cd:plunder_match:{0}:{1}:{2}'.format(self.server_id, self.char_id, self.rival_id)


# 聊天CD
class ChatCD(CD):
    __slots__ = []

    def make_key(self):
        return 'cd:chat:{0}:{1}'.format(self.server_id, self.char_id)


# 公会探索CD
class UnionExploreCD(CD):
    __slots__ = []

    def make_key(self):
        return 'cd:union_explore:{0}:{1}'.format(self.server_id, self.char_id)


# 排行榜聊天CD
class LeaderboardArenaChatCD(CD):
    __slots__ = []

    def make_key(self):
        return 'cd:lbarenachat:{0}:{1}'.format(self.server_id, self.char_id)


class LeaderboardPlunderChatCD(CD):
    __slots__ = []

    def make_key(self):
        return 'cd:lbplunderchat:{0}:{1}'.format(self.server_id, self.char_id)


class LeaderboardChampionshipChatCD(CD):
    __slots__ = []

    def make_key(self):
        return 'cd:lbchampionshipchat:{0}:{1}'.format(self.server_id, self.char_id)
