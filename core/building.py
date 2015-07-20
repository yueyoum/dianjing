# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       building
Date Created:   2015-07-21 00:33
Description:

"""

from core.db import get_mongo_db
from core.mongo import Document

from config import ConfigBuilding

from utils.message import MessagePipe

from protomsg.building_pb2 import BuildingNotify

class BuildingManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id
        self.mongo = get_mongo_db(server_id)

        if not self.mongo.building.find_one({'_id': self.char_id}):
            doc = Document.get("building")
            doc['_id'] = self.char_id

            self.mongo.building.insert_one(doc)


    def buy_training(self, training_id):
        # TODO cost
        # TODO check training_id exists?
        self.mongo.character.update_one(
            {'_id': self.char_id},
            {'$push': {'own_training_ids', training_id}}
        )


    def level_up(self, building_id):
        # TODO error
        # TODO cost
        b = ConfigBuilding.get(building_id)
        if not b.max_levels:
            raise RuntimeError("can not levelup")

        buildings = self.mongo.building.find_one({'_id': self.char_id}, {'buildings.{0}'.format(building_id): 1})
        current_level = buildings['buildings'].get(str(building_id), 1)
        if current_level >= b.max_levels:
            raise RuntimeError("already max level")

        self.mongo.building.update_one(
            {'_id': self.char_id},
            {'$inc': {'building.{0}'.format(building_id): 1}}
        )

        self.send_notify()


    def send_notify(self):
        notify = BuildingNotify()

        buildings = self.mongo.building.find_one({'_id': self.char_id}, {'buildings': 1})

        for b in ConfigBuilding.all_values():
            notify_building = notify.buildings.add()
            notify_building.id = b.id
            if not b.max_levels:
                notify_building.level = 0
            else:
                notify_building.level = buildings['builds'].get(str(b.id), 1)

        MessagePipe(self.char_id).put(msg=notify)

