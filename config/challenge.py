# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2015-07-15 10:36
Description:

"""

from config.base import ConfigBase

class ChallengeType(object):
    __slots__ = [
        'id', 'level'
    ]

class ChallengeMatch(object):
    __slots__ = [
        'id', 'next_id', 'tp', 'policy', 'level', 'strength', 'staffs',
        'club_name', 'club_flag'
    ]

    def __init__(self):
        self.id = None
        self.next_id = None
        self.tp = None
        self.policy = None
        self.level = None
        self.strength = None
        self.staffs = None
        self.club_name = None
        self.club_flag = None
    

class ConfigChallengeType(ConfigBase):
    EntityClass = ChallengeType
    INSTANCES = {}
    FILTER_CACHE = {}
    
    @classmethod
    def get(cls, id):
        """

        :rtype : ChallengeType
        """
        return super(ConfigChallengeType, cls).get(id)


class ConfigChallengeMatch(ConfigBase):
    EntityClass = ChallengeMatch
    INSTANCES = {}
    FILTER_CACHE = {}

    FIRST_ID = None
    LAST_ID = None

    @classmethod
    def initialize(cls, fixture):
        super(ConfigChallengeMatch, cls).initialize(fixture)

        values = cls.INSTANCES.values()
        for i in values:
            if i.next_id == 0:
                cls.LAST_ID = i.id
                break
        else:
            raise RuntimeError("ConfigChallengeMatch, can not find LAST ID")

        match_id = cls.LAST_ID
        while True:
            for i in values:
                if i.next_id == match_id:
                    match_id = i.id
                    break
            else:
                cls.FIRST_ID = match_id
                break


    @classmethod
    def get(cls, id):
        """

        :rtype : ChallengeMatch
        """
        return super(ConfigChallengeMatch, cls).get(id)
