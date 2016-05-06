# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       tower
Date Created:   2016-05-05 15-46
Description:

"""
from dianjing.exception import GameException

from core.mongo import MongoTower
from core.club import Club
from core.match import ClubMatch
from core.resource import ResourceClassification

from utils.message import MessagePipe

from config import ConfigTowerLevel, ConfigErrorMessage
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

    def match(self, level):
        config = ConfigTowerLevel.get(level)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_LEVEL_NOT_EXISTS"))

        star = self.doc['levels'].get(str(level), None)
        if star is None:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_LEVEL_NOT_OPENED"))

        if star > 0:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_LEVEL_ALREADY_MATCHED"))

        club_one = Club(self.server_id, self.char_id)
        club_two = config.make_club()
        club_match = ClubMatch(club_one, club_two)
        msg = club_match.start()
        msg.key = str(level)
        return msg

    def report(self, key, star):
        level = int(key)
        config = ConfigTowerLevel.get(level)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if star == 0:
            star = -1

        self.doc['levels'][str(level)] = star

        update_levels = [level]
        updater = {'levels.{0}'.format(level): star}

        if star > 0 and level < MAX_LEVEL:
            next_level = level + 1
            self.doc['levels'][str(next_level)] = 0

            update_levels.append(next_level)
            updater['levels.{0}'.format(next_level)] = 0

        if star == 3 and level > self.doc['max_star_level']:
            self.doc['max_star_level'] = level
            updater['max_star_level'] = level

        MongoTower.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        resource_classified = ResourceClassification.classify(config.get_star_reward(star))
        resource_classified.add(self.server_id, self.char_id)

        self.send_notify(act=ACT_UPDATE, levels=update_levels)
        # TODO
        return resource_classified, False

    def reset(self):
        if -1 not in self.doc['levels'].values():
            # 没有失败的不能重置
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_CANNOT_RESET_NO_FAILURE"))

        self.doc['levels'] = {'1': 0}
        self.doc['talents'] = []
        self.doc['star'] = 0

        MongoTower.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'levels': self.doc['levels'],
                'talents': self.doc['talents'],
                'star': self.doc['star'],
            }}
        )

        self.send_notify()

    def to_max_star_level(self):
        if not self.doc['max_star_level']:
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_NO_MAX_STAR_LEVEL"))

        if -1 in self.doc['levels'].values():
            raise GameException(ConfigErrorMessage.get_error_id("TOWER_CANNOT_TO_MAX_LEVEL_HAS_FAILURE"))

        levels = {}
        for i in range(1, self.doc['max_star_level'] + 1):
            levels[str(i)] = 3

        if self.doc['max_star_level'] < MAX_LEVEL:
            levels[str(self.doc['max_star_level'] + 1)] = 0

        self.doc['levels'] = levels
        MongoTower.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'levels': levels
            }}
        )

        self.send_notify()

        # TODO drop

    def send_notify(self, act=ACT_INIT, levels=None):
        notify = TowerNotify()
        notify.act = act
        notify.star = self.doc['star']
        notify.rank = self.get_rank()
        notify.talent_ids.extend(self.doc['talents'])

        # TODO
        notify.reset_times = 10

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
