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
from core.club import Club, get_club_property
from core.value_log import ValueLogDungeonMatchTimes, ValueLogDungeonBuyTimes
from core.resource import ResourceClassification, money_text_to_item_id
from core.vip import VIP
from core.energy import Energy
from core.formation import Formation

from protomsg.dungeon_pb2 import DungeonNotify
from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT

from utils.message import MessagePipe

DUNGEON_FREE_TIMES = 1


def get_opened_category_ids():
    today = arrow.utcnow().to(settings.TIME_ZONE).weekday() + 1
    ids = []
    for k, v in ConfigDungeon.INSTANCES.iteritems():
        if today in v.open_time:
            ids.append(k)

    return ids


class TimesInfo(object):
    __slots__ = ['match_times', 'buy_times', 'remained_match_times', 'remained_buy_times', 'buy_cost']

    def __init__(self, server_id, char_id, category_id):
        self.match_times = ValueLogDungeonMatchTimes(server_id, char_id).count_of_today(sub_id=category_id)
        self.buy_times = ValueLogDungeonBuyTimes(server_id, char_id).count_of_today(sub_id=category_id)

        self.remained_match_times = DUNGEON_FREE_TIMES + self.buy_times - self.match_times
        if self.remained_match_times < 0:
            self.remained_match_times = 0

        self.remained_buy_times = VIP(server_id, char_id).dungeon_reset_times - self.buy_times
        if self.remained_buy_times < 0:
            self.remained_buy_times = 0

        self.buy_cost = ConfigDungeonBuyCost.get_cost(category_id, self.buy_times + 1)


class Dungeon(object):
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def get_dungeon_today_times(self, category_id):
        return ValueLogDungeonMatchTimes(self.server_id, self.char_id).count_of_today(sub_id=category_id)

    def buy_times(self, category_id, send_notify=True):
        ri = TimesInfo(self.server_id, self.char_id, category_id)
        if not ri.remained_buy_times:
            raise GameException(ConfigErrorMessage.get_error_id("DUNGEON_NO_BUY_TIMES"))

        cost = [(money_text_to_item_id('diamond'), ri.buy_cost), ]
        rc = ResourceClassification.classify(cost)
        rc.check_exist(self.server_id, self.char_id)
        rc.remove(self.server_id, self.char_id, message="Dungeon.buy_times:{0}".format(category_id))

        ValueLogDungeonBuyTimes(self.server_id, self.char_id).record(sub_id=category_id)

        if send_notify:
            self.send_notify(category_id=category_id)

    def start(self, dungeon_id, formation_slots=None):
        grade_conf = ConfigDungeonGrade.get(dungeon_id)
        if not grade_conf:
            raise GameException(ConfigErrorMessage.get_error_id("DUNGEON_NOT_EXIST"))

        map_name = ConfigDungeon.get(grade_conf.belong).map_name

        club_level = get_club_property(self.server_id, self.char_id, 'level')
        if grade_conf.need_level > club_level:
            raise GameException(ConfigErrorMessage.get_error_id("DUNGEON_CLUB_LEVEL_NOT_ENOUGH"))

        f = Formation(self.server_id, self.char_id)
        if formation_slots:
            f.sync_slots(formation_slots)

        Energy(self.server_id, self.char_id).check(ConfigDungeon.get(grade_conf.belong).cost)

        ri = TimesInfo(self.server_id, self.char_id, grade_conf.belong)
        if not ri.remained_match_times:
            # 购买
            self.buy_times(grade_conf.belong)

        club_one = Club(self.server_id, self.char_id)
        club_two = ConfigNPCFormation.get(grade_conf.npc)
        msg = ClubMatch(club_one, club_two, 6, f.get_skill_sequence(), {}).start()
        msg.key = str(dungeon_id)
        msg.map_name = map_name
        return msg

    def report(self, key, star):
        grade_id = int(key)
        conf = ConfigDungeonGrade.get(grade_id)
        if star > 0:
            Energy(self.server_id, self.char_id).remove(ConfigDungeon.get(conf.belong).cost)
            ValueLogDungeonMatchTimes(self.server_id, self.char_id).record(sub_id=conf.belong, value=1)

            resource_classified = ResourceClassification.classify(conf.get_drop())
            resource_classified.add(self.server_id, self.char_id, message="Dungeon.report:{0}".format(grade_id))
            ret = resource_classified
        else:
            ret = None

        self.send_notify(conf.belong)
        return ret

    def send_notify(self, category_id=None):
        if category_id:
            act = ACT_UPDATE
            ids = [category_id]
        else:
            act = ACT_INIT
            ids = get_opened_category_ids()

        match_times = ValueLogDungeonMatchTimes(self.server_id, self.char_id).batch_count_of_today()
        buy_times = ValueLogDungeonBuyTimes(self.server_id, self.char_id).batch_count_of_today()
        total_reset_times = VIP(self.server_id, self.char_id).dungeon_reset_times

        def _get_remained_match_times(_id):
            _id = str(_id)
            remained = DUNGEON_FREE_TIMES + buy_times.get(_id, 0) - match_times.get(_id, 0)
            if remained < 0:
                remained = 0

            return remained

        def _get_remained_buy_times(_id):
            remained = total_reset_times - buy_times.get(str(_id), 0)
            if remained < 0:
                return remained

            return remained

        def _get_buy_cost(_id):
            return ConfigDungeonBuyCost.get_cost(_id, buy_times.get(str(_id), 0)+1)

        notify = DungeonNotify()
        notify.act = act

        for i in ids:
            notify_info = notify.info.add()
            notify_info.id = i
            notify_info.free_times = _get_remained_match_times(i)
            notify_info.buy_times = _get_remained_buy_times(i)
            notify_info.buy_cost = _get_buy_cost(i)

        MessagePipe(self.char_id).put(msg=notify)
