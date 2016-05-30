# -*- coding: utf-8 -*-
"""
Author:         ouyang
Filename:       dungeon
Date Created:   2016-04-25 03:19
Description:

"""
import arrow

from django.conf import settings

from dianjing.exception import GameException

from config import ConfigDungeon, ConfigDungeonGrade, ConfigErrorMessage, ConfigNPCFormation, ConfigDungeonBuyCost

from core.match import ClubMatch
from core.club import Club
from core.value_log import ValueLogDungeonMatchTimes
from core.resource import ResourceClassification

from protomsg.dungeon_pb2 import DungeonNotify
from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT

from utils.message import MessagePipe

DUNGEON_FREE_TIMES = 1


def get_opened_category_ids():
    today = arrow.utcnow().to(settings.TIME_ZONE).weekday()
    ids = []
    for k, v in ConfigDungeon.INSTANCES.iteritems():
        if today in v.open_time:
            ids.append(k)

    return ids


class Dungeon(object):
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def get_dungeon_today_times(self, category_id):
        return ValueLogDungeonMatchTimes(self.server_id, self.char_id).count_of_today(sub_id=category_id)

    def start(self, dungeon_id):
        grade_conf = ConfigDungeonGrade.get(dungeon_id)
        if not grade_conf:
            raise GameException(ConfigErrorMessage.get_error_id("DUNGEON_NOT_EXIST"))

        club_one = Club(self.server_id, self.char_id)

        if grade_conf.need_level > club_one.level:
            raise GameException(ConfigErrorMessage.get_error_id("DUNGEON_CLUB_LEVEL_NOT_ENOUGH"))

        # TODO: energy check
        # conf = ConfigDungeon.get(grade_conf.belong)
        # if conf.cost:
        #     raise GameException(ConfigErrorMessage.get_error_id("DUNGEON_ENERGY_NOT_ENOUGH"))

        today_times = ValueLogDungeonMatchTimes(self.server_id, self.char_id).count_of_today(sub_id=grade_conf.belong)
        if today_times >= DUNGEON_FREE_TIMES:
            # TODO 购买
            pass
        else:
            pass

        club_two = ConfigNPCFormation.get(grade_conf.npc)
        msg = ClubMatch(club_one, club_two).start()
        msg.key = str(dungeon_id)
        return msg

    def report(self, key, star):
        grade_id = int(key)
        conf = ConfigDungeonGrade.get(grade_id)

        ValueLogDungeonMatchTimes(self.server_id, self.char_id).record(sub_id=conf.belong, value=1)
        self.send_notify(conf.belong)

        if star > 0:
            # TODO: remove energy
            resource_classified = ResourceClassification.classify(conf.drop)
            resource_classified.add(self.server_id, self.char_id)
            return resource_classified

        return None

    def send_notify(self, category_id=None):
        if category_id:
            act = ACT_UPDATE
            ids = [category_id]
        else:
            act = ACT_INIT
            ids = get_opened_category_ids()

        notify = DungeonNotify()
        notify.act = act

        all_times = ValueLogDungeonMatchTimes(self.server_id, self.char_id).batch_count_of_today()

        for i in ids:
            notify_info = notify.info.add()
            notify_info.id = i
            notify_info.free_times = DUNGEON_FREE_TIMES - all_times.get(str(i), 0)
            # TODO
            notify_info.buy_times = 10
            notify_info.buy_cost = ConfigDungeonBuyCost.get_cost(10)

        MessagePipe(self.char_id).put(msg=notify)
