# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       building
Date Created:   2015-07-21 00:33
Description:

"""

from dianjing.exception import GameException

from core.mongo import MongoBuilding
from core.club import Club
from core.resource import Resource

from config import ConfigBuilding, ConfigErrorMessage

from utils.message import MessagePipe

from protomsg.building_pb2 import BuildingNotify
from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT

BUILDING_HEADQUARTERS = 1  # 总部大楼
BUILDING_TRAINING_CENTER = 2  # 任务中心
BUILDING_STAFF_CENTER = 3  # 员工中心
BUILDING_TASK_CENTER = 4  # 任务中心
BUILDING_LEAGUE_CENTER = 5  # 联赛中心


class BuildingManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        doc = MongoBuilding.db(server_id).find_one({'_id': self.char_id})
        if not doc:
            doc = MongoBuilding.document()
            doc['_id'] = self.char_id
            doc['buildings'] = {str(i): 1 for i in ConfigBuilding.INSTANCES.keys()}
            MongoBuilding.db(server_id).insert_one(doc)
        else:
            updater = {}
            for i in ConfigBuilding.INSTANCES.keys():
                if str(i) not in doc['buildings']:
                    updater['buildings.{0}'.format(i)] = 1

            if updater:
                MongoBuilding.db(server_id).update_one(
                    {'_id': self.char_id},
                    {'$set': updater}
                )

    def get_level(self, building_id):
        doc = MongoBuilding.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'buildings.{0}'.format(building_id): 1}
        )

        return doc['buildings'][str(building_id)]

    def level_up(self, building_id):
        b = ConfigBuilding.get(building_id)
        if not b:
            raise GameException(ConfigErrorMessage.get_error_id("BUILDING_NOT_EXIST"))

        if not b.max_levels:
            raise GameException(ConfigErrorMessage.get_error_id("BUILDING_CAN_NOT_LEVEL_UP"))

        current_level = self.get_level(building_id)
        if current_level >= b.max_levels:
            raise GameException(ConfigErrorMessage.get_error_id("BUILDING_ALREADY_MAX_LEVEL"))

        if Club(self.server_id, self.char_id).level < b.get_level(current_level).up_need_club_level:
            raise GameException(ConfigErrorMessage.get_error_id("CLUB_LEVEL_NOT_ENOUGH"))

        check = {
            "gold": -b.get_level(current_level).up_need_gold,
            "message": u"Building {0} level up to {1}".format(building_id, current_level+1)
        }

        with Resource(self.server_id, self.char_id).check(**check):
            MongoBuilding.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$inc': {'buildings.{0}'.format(building_id): 1}}
            )

        self.send_notify(building_ids=[building_id])

    def send_notify(self, building_ids=None):
        if building_ids:
            projection = {'buildings.{0}'.format(i): 1 for i in building_ids}
            act = ACT_UPDATE
        else:
            projection = {'buildings': 1}
            act = ACT_INIT

        doc = MongoBuilding.db(self.server_id).find_one({'_id': self.char_id}, projection)
        notify = BuildingNotify()
        notify.act = act

        for b in ConfigBuilding.all_values():
            if building_ids and b.id not in building_ids:
                continue

            notify_building = notify.buildings.add()
            notify_building.id = b.id
            notify_building.level = doc['buildings'][str(b.id)]

        MessagePipe(self.char_id).put(msg=notify)


class BuildingBase(object):
    BUILDING_ID = 0

    def __init__(self, server_id, char_id):
        self.bm = BuildingManager(server_id, char_id)

    def get_level(self):
        return self.bm.get_level(self.BUILDING_ID)

    def level_up(self):
        return self.bm.level_up(self.BUILDING_ID)


class BuildingTrainingCenter(BuildingBase):
    BUILDING_ID = BUILDING_TRAINING_CENTER


class BuildingStaffCenter(BuildingBase):
    BUILDING_ID = BUILDING_STAFF_CENTER


class BuildingTaskCenter(BuildingBase):
    BUILDING_ID = BUILDING_TASK_CENTER


class BuildingLeagueCenter(BuildingBase):
    BUILDING_ID = BUILDING_LEAGUE_CENTER
