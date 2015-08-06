# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       building
Date Created:   2015-07-21 00:33
Description:

"""

from dianjing.exception import GameException


from core.db import MongoDB
from core.mongo import Document
from core.club import Club
from core.resource import Resource

from config import ConfigBuilding, ConfigErrorMessage

from utils.message import MessagePipe

from protomsg.building_pb2 import BuildingNotify

class BuildingManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = MongoDB.get(server_id)

        if not self.mongo.building.find_one({'_id': self.char_id}, {'_id': 1}):
            doc = Document.get("building")
            doc['_id'] = self.char_id

            self.mongo.building.insert_one(doc)


    def get_level(self, building_id):
        doc = self.mongo.building.find_one(
            {'_id': self.char_id},
            {'buildings.{0}'.format(building_id): 1}
        )

        return doc['buildings'].get(str(building_id), 1)


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

        needs = {"gold": -b.get_level(current_level).up_need_gold}
        with Resource(self.server_id, self.char_id).check(**needs):
            self.mongo.building.update_one(
                {'_id': self.char_id},
                {'$inc': {'buildings.{0}'.format(building_id): 1}}
            )

        self.send_notify(building_ids=[building_id])


    def send_notify(self, building_ids=None):
        if building_ids:
            projection = {'buildings.{0}'.format(i): 1 for i in building_ids}
        else:
            projection = {'buildings': 1}


        notify = BuildingNotify()
        buildings = self.mongo.building.find_one({'_id': self.char_id}, projection)

        for b in ConfigBuilding.all_values():
            if building_ids and b.id not in building_ids:
                continue

            notify_building = notify.buildings.add()
            notify_building.id = b.id
            if not b.max_levels:
                notify_building.level = 0
            else:
                notify_building.level = buildings['buildings'].get(str(b.id), 1)

        MessagePipe(self.char_id).put(msg=notify)

