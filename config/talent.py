"""
Author:         ouyang
Filename:       talent
Date Created:   2016-04-14 18:40
Description:

"""

from config.base import ConfigBase


class Talent(object):
    __slots__ = ["id", "next_id", "tp", "effect_id", "unlock",
                 "up_need", "trigger_unlock"]

    def __init__(self):
        self.id = 0
        self.next_id = 0
        self.tp = 0
        self.effect_id = 0
        self.unlock = 0
        self.up_need = 0
        self.trigger_unlock = []


class ConfigTalent(ConfigBase):
    EntityClass = Talent
    INSTANCES = {}
    """:type: dict[int, Talent]"""
    FILTER_CACHE = {}

    INIT_TALENT_IDS = []

    @classmethod
    def initialize(cls, fixture):
        super(ConfigTalent, cls).initialize(fixture)
        for k, v in cls.INSTANCES.iteritems():
            if v.unlock == 0:
                cls.INIT_TALENT_IDS.append(k)

    @classmethod
    def get(cls, _id):
        """

        :rtype: Talent
        """
        return super(ConfigTalent, cls).get(_id)
