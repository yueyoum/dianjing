# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_building
Date Created:   2015-08-06 10:21
Description:

"""

import random

from dianjing.exception import GameException

from core.mongo import MongoBuilding, MongoCharacter

from core.building import BuildingManager

from config import ConfigErrorMessage, ConfigBuilding


def set_building_level(building_id, level):
    MongoBuilding.db(1).update_one(
        {'_id': 1},
        {'$set': {'buildings.{0}.current_level'.format(building_id): level,
                  'buildings.{0}.complete_time'.format(building_id): -1}},
        upsert=True
    )


def get_random_valid_building():
    while True:
        b = random.choice(ConfigBuilding.INSTANCES.values())
        b_cfg = ConfigBuilding.get(b.id)
        need_club_level = b_cfg.get_level(b.max_levels - 1).up_need_club_level
        need_gold = b_cfg.get_level(b.max_levels - 1).up_need_gold
        if need_gold > 0 and need_club_level >= b.max_levels - 1:
            return b, need_club_level, need_gold


def get_not_exist_building():
    for i in range(1, 1000):
        if i not in ConfigBuilding.INSTANCES.keys():
            return i


class TestBuilding(object):
    def reset(self):
        MongoBuilding.db(1).building.delete_one({'_id': 1})

    def setUp(self):
        self.reset()
        BuildingManager(1, 1)

    def tearDown(self):
        self.reset()
        MongoBuilding.db(1).drop()

    def test_getLevel(self):
        b, need_club_level, need_gold = get_random_valid_building()
        set_building_level(b.id, b.max_levels)
        assert BuildingManager(1, 1).get_level(b.id) == b.max_levels

    def test_send_notify(self):
        BuildingManager(1, 1).send_notify()

    def test_level_up_building_not_exist(self):
        building_id = get_not_exist_building()

        try:
            BuildingManager(1, 1).level_up(building_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("BUILDING_NOT_EXIST")
        else:
            raise Exception("can not be here!")

    def test_level_up_already_max_level(self):
        b, need_club_level, need_gold = get_random_valid_building()
        set_building_level(b.id, b.max_levels)
        try:
            BuildingManager(1, 1).level_up(b.id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("BUILDING_ALREADY_MAX_LEVEL")
        else:
            raise Exception("can not be here!")

    def test_level_up_club_level_not_enough(self):
        b, need_club_level, need_gold = get_random_valid_building()
        set_building_level(b.id, b.max_levels - 1)

        MongoCharacter.db(1).update_one(
            {'_id': 1},
            {'$set': {'club.level': need_club_level - 1}}
        )
        try:
            BuildingManager(1, 1).level_up(b.id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("CLUB_LEVEL_NOT_ENOUGH")
        else:
            raise Exception("can not be here!")

    def test_level_up_gold_not_enough(self):
        b, need_club_level, need_gold = get_random_valid_building()
        set_building_level(b.id, b.max_levels - 1)

        MongoCharacter.db(1).update_one(
            {'_id': 1},
            {'$set': {'club.level': need_club_level}}
        )

        try:
            BuildingManager(1, 1).level_up(b.id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("GOLD_NOT_ENOUGH")
        else:
            raise Exception("can not be here!")

    def test_level_up(self):
        b, need_club_level, need_gold = get_random_valid_building()
        set_building_level(b.id, b.max_levels - 1)

        MongoCharacter.db(1).update_one(
            {'_id': 1},
            {'$set': {
                'club.level': need_club_level,
                'club.gold': need_gold
            }}
        )

        BuildingManager(1, 1).level_up(b.id)
        data = MongoBuilding.db(1).find_one({'_id': 1}, {'buildings.{0}'.format(b.id): 1})
        assert data['buildings'][str(b.id)]['complete_time'] != -1
        assert MongoCharacter.db(1).find_one({'_id': 1})['club']['gold'] == 0

    def test_levelComfirm(self):
        b, need_club_level, need_gold = get_random_valid_building()
        set_building_level(b.id, b.max_levels - 1)

        MongoCharacter.db(1).update_one(
            {'_id': 1},
            {'$set': {
                'club.level': need_club_level,
                'club.gold': need_gold
            }}
        )

        BuildingManager(1, 1).level_up(b.id)
        MongoBuilding.db(1).update_one(
            {'_id': 1},
            {'$set': {'buildings.{0}.complete_time'.format(b.id): 0}}
        )
        BuildingManager(1, 1).levelup_confirm()
        data = MongoBuilding.db(1).find_one({'_id': 1}, {'buildings.{0}'.format(b.id): 1})
        assert data['buildings'][str(b.id)]['complete_time'] == -1
        assert BuildingManager(1, 1).get_level(b.id) == b.max_levels
