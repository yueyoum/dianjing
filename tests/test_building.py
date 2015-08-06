# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_building
Date Created:   2015-08-06 10:21
Description:

"""

import random

from dianjing.exception import GameException

from core.db import MongoDB

from core.building import BuildingManager

from config import ConfigErrorMessage, ConfigBuilding


class TestBuilding(object):
    def reset(self):
        MongoDB.get(1).building.delete_one({'_id': 1})
        MongoDB.get(1).character.update_one(
            {'_id': 1},
            {'$set': {
                'club.gold': 0,
                'club.level': 1
            }}
        )


    def setUp(self):
        self.reset()

    def tearDown(self):
        self.reset()


    def test_send_notify(self):
        BuildingManager(1, 1).send_notify()

    def test_level_up_not_exist(self):
        try:
            BuildingManager(1, 1).level_up(9999)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("BUILDING_NOT_EXIST")
        else:
            raise Exception("can not be here!")


    def test_level_up_already_max_level(self):
        b = random.choice(ConfigBuilding.INSTANCES.values())

        MongoDB.get(1).building.update_one(
            {'_id': 1},
            {'$set': {'buildings.{0}'.format(b.id): b.max_levels}},
            upsert=True
        )

        try:
            BuildingManager(1, 1).level_up(b.id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("BUILDING_ALREADY_MAX_LEVEL")
        else:
            raise Exception("can not be here!")

    def test_level_up_club_level_not_enough(self):
        b = random.choice(ConfigBuilding.INSTANCES.values())

        level = b.max_levels - 1

        MongoDB.get(1).building.update_one(
            {'_id': 1},
            {'$set': {'buildings.{0}'.format(b.id): level}},
            upsert=True
        )

        try:
            BuildingManager(1, 1).level_up(b.id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("CLUB_LEVEL_NOT_ENOUGH")
        else:
            raise Exception("can not be here!")


    def test_level_up_gold_not_enough(self):
        b = random.choice(ConfigBuilding.INSTANCES.values())

        level = b.max_levels - 1

        MongoDB.get(1).building.update_one(
            {'_id': 1},
            {'$set': {'buildings.{0}'.format(b.id): level}},
            upsert=True
        )

        club_level = b.get_level(level).up_need_club_level
        MongoDB.get(1).character.update_one(
            {'_id': 1},
            {'$set': {'club.level': club_level}}
        )

        try:
            BuildingManager(1, 1).level_up(b.id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("GOLD_NOT_ENOUGH")
        else:
            raise Exception("can not be here!")


    def test_level_up(self):
        b = random.choice(ConfigBuilding.INSTANCES.values())

        level = b.max_levels - 1

        MongoDB.get(1).building.update_one(
            {'_id': 1},
            {'$set': {'buildings.{0}'.format(b.id): level}},
            upsert=True
        )

        club_level = b.get_level(level).up_need_club_level
        gold = b.get_level(level).up_need_gold

        MongoDB.get(1).character.update_one(
            {'_id': 1},
            {'$set': {
                'club.level': club_level,
                'club.gold': gold
            }}
        )

        BuildingManager(1, 1).level_up(b.id)

        assert BuildingManager(1, 1).get_level(b.id) == b.max_levels
        assert MongoDB.get(1).character.find_one({'_id': 1})['club']['gold'] == 0

