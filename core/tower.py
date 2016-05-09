# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       tower
Date Created:   2016-05-05 15-46
Description:

"""
import random

from dianjing.exception import GameException

from core.mongo import MongoTower
from core.club import Club
from core.match import ClubMatch
from core.resource import ResourceClassification, money_text_to_item_id
from core.times_log import TimesLogTowerResetTimes

from utils.message import MessagePipe

from config import ConfigTowerLevel, ConfigErrorMessage, ConfigTowerResetCost
from protomsg.tower_pb2 import (
    TowerNotify,
    TOWER_LEVEL_CURRENT,
    TOWER_LEVEL_FAILURE,
    TOWER_LEVEL_NOT_OPEN,
    TOWER_LEVEL_PASSED,
)

from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT

MAX_LEVEL = max(ConfigTowerLevel.INSTANCES.keys())

class Tower(object):
    __slots__ = ['server_id', 'char_id', 'doc']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.doc = MongoTower.db(self.server_id).find_one({'_id': self.char_id})
        if not self.doc:
            self.doc = MongoTower.document()
            self.doc['_id'] = self.char_id
            self.doc['levels'] = {'1': 0}
            MongoTower.db(self.server_id).insert_one(self.doc)

    def get_rank(self):
        # XXX
        doc = MongoTower.db(self.server_id).find({'star': {'$gt': self.doc['star']}})
        return doc.count() + 1

    def get_current_level(self):
        for k, v in self.doc['levels'].iteritems():
            if v == 0:
                return int(k)

        return 0

    def is_all_complete(self):
        # 0　表示可以打，　-1 表示失败，　不能打的没有记录，　这里就用-2表示
        return self.doc['levels'].get(str(MAX_LEVEL), -2) > 0


    def get_today_reset_times(self):
        return TimesLogTowerResetTimes(self.server_id, self.char_id).count_of_today()

    def get_total_reset_times(self):
        # TODO vip reset times
        return 10

    def remained_reset_times(self):
        remained = self.get_today_reset_times() - self.get_today_reset_times()
        if remained < 0:
            remained = 0

        return remained

    def match(self):
        level = self.get_current_level()
        if not level:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_ALREADY_ALL_PASSED"))

        config = ConfigTowerLevel.get(level)

        club_one = Club(self.server_id, self.char_id)
        club_two = config.make_club()
        club_match = ClubMatch(club_one, club_two)
        msg = club_match.start()
        msg.key = str(level)
        return msg

    def report(self, key, star):
        if star not in [1, 2, 3]:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        level = int(key)
        config = ConfigTowerLevel.get(level)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        self.doc['levels'][str(level)] = star

        update_levels = [level]
        self.doc['star'] += star

        updater = {
            'levels.{0}'.format(level): star,
            'star': self.doc['star'],
        }

        if star == 0:
            star = -1

        if star > 0 and level < MAX_LEVEL:
            next_level = level + 1
            self.doc['levels'][str(next_level)] = 0

            update_levels.append(next_level)
            updater['levels.{0}'.format(next_level)] = 0

        if star == 3 and level == self.doc['max_star_level']+1:
            self.doc['max_star_level'] = level
            updater['max_star_level'] = level

        # 转盘信息
        turntable = config.get_turntable()
        if turntable:
            all_list = []
            for _, v in turntable.iteritems():
                all_list.extend(v)

            random.shuffle(all_list)

            turntable['all_list'] = all_list
            updater['turntable'] = turntable
        else:
            all_list = []
            updater['turntable'] = {}

        MongoTower.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        resource_classified = ResourceClassification.classify(config.get_star_reward(star))
        resource_classified.add(self.server_id, self.char_id)

        self.send_notify(act=ACT_UPDATE, levels=update_levels)
        return resource_classified, self.doc['star'], all_list

    def reset(self):
        current_reset_times = self.get_today_reset_times()
        if current_reset_times >= self.get_total_reset_times():
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_NO_RESET_TIMES"))

        if -1 not in self.doc['levels'].values() or not self.is_all_complete():
            # 没有失败的不能重置 或者没有打完
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_CANNOT_RESET_NO_FAILURE"))

        config = ConfigTowerResetCost.get(current_reset_times)
        if config.cost:
            cost = [(money_text_to_item_id('diamond'), config.cost)]

            resource_classified = ResourceClassification.classify(cost)
            resource_classified.check_exist(self.server_id, self.char_id)
            resource_classified.remove(self.server_id, self.char_id)

        self.doc['levels'] = {'1': 0}
        self.doc['talents'] = []
        self.doc['star'] = 0

        MongoTower.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'levels': self.doc['levels'],
                'talents': self.doc['talents'],
                'star': self.doc['star'],
                'turntable': {},
            }}
        )

        TimesLogTowerResetTimes(self.server_id, self.char_id).record()
        self.send_notify()

    def to_max_star_level(self):
        if not self.doc['max_star_level']:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_NO_MAX_STAR_LEVEL"))

        if -1 in self.doc['levels'].values():
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_CANNOT_TO_MAX_LEVEL_HAS_FAILURE"))

        drops = {}

        levels = {}
        for i in range(1, self.doc['max_star_level'] + 1):
            levels[str(i)] = 3

            for _id, _amount in ConfigTowerLevel.get(i).get_star_reward(3):
                if _id in drops:
                    drops[_id] += _amount
                else:
                    drops[_id] = _amount

        inc_star = len(levels) * 3

        if self.doc['max_star_level'] < MAX_LEVEL:
            levels[str(self.doc['max_star_level'] + 1)] = 0

        self.doc['levels'] = levels
        self.doc['star'] += inc_star
        MongoTower.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'levels': levels,
                'star': self.doc['star']
            }}
        )

        self.send_notify()

        resource_classified = ResourceClassification.classify(drops.items())
        resource_classified.add(self.server_id, self.char_id)
        return resource_classified


    def turntable_pick(self, star):
        if star not in [3, 6, 9]:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if star < self.doc['star']:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_STAR_NOT_ENOUGH"))

        turntable = self.doc.get('turntable', {})
        if not turntable:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        got = random.choice(turntable[str(star)])
        index = turntable['all_list'].index(got)

        self.doc['star'] -= star
        self.doc['talents'].append(got)

        MongoTower.db(self.server_id).update_one(
            {'_id': self.char_id},
            {
                '$set': {
                    'star': self.doc['star'],
                    'talents': self.doc['talents'],
                    'turntable': {},
                }
            }
        )

        self.send_notify(act=ACT_UPDATE, levels=[])
        return index


    def send_notify(self, act=ACT_INIT, levels=None):
        notify = TowerNotify()
        notify.act = act
        notify.star = self.doc['star']
        notify.rank = self.get_rank()
        notify.talent_ids.extend(self.doc['talents'])

        notify.reset_times = self.remained_reset_times()

        if levels is None:
            # 全部发送
            levels = ConfigTowerLevel.INSTANCES.keys()

        for lv in levels:
            notify_level = notify.levels.add()
            notify_level.level = int(lv)

            star = self.doc['levels'].get(str(lv), None)
            if star is None:
                notify_level.status = TOWER_LEVEL_NOT_OPEN
            elif star == -1:
                notify_level.status = TOWER_LEVEL_FAILURE
            elif star == 0:
                notify_level.status = TOWER_LEVEL_CURRENT
            else:
                notify_level.status = TOWER_LEVEL_PASSED
                notify_level.star = star

        MessagePipe(self.char_id).put(msg=notify)
