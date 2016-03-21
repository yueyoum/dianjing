# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2015-07-15 10:36
Description:

"""

from config.base import ConfigBase


class Chapter(object):
    __slots__ = [
        'id', 'tp', 'star_reward'
    ]

    def __init__(self):
        self.id = 0
        self.tp = 0
        self.star_reward = []


class ChallengeMatch(object):
    __slots__ = [
        'id', 'chapter', 'name', 'club_flag', 'energy', 'club_exp', 'staffs', 'drop',
        'condition_challenge', 'times_limit', 'next',
    ]

    def __init__(self):
        self.id = 0
        self.chapter = 0
        self.name = ""
        self.club_flag = ""
        self.energy = 0
        self.club_exp = 0
        self.staffs = 0
        self.drop = 0
        self.condition_challenge = 0
        self.times_limit = 0
        self.next = []


class ConfigChapter(ConfigBase):
    EntityClass = Chapter
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, _id):
        """

        :rtype: Chapter
        """
        return super(ConfigChapter, cls).get(_id)

class ConfigChallengeMatch(ConfigBase):
    EntityClass = ChallengeMatch
    INSTANCES = {}
    FILTER_CACHE = {}

    @classmethod
    def get(cls, id):
        """

        :rtype : ChallengeMatch
        """
        return super(ConfigChallengeMatch, cls).get(id)
