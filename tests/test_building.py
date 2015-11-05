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
        {'$set': {'buildings.{0}.level'.format(building_id): level,
                  'buildings.{0}.end_at'.format(building_id): 0}},
        upsert=True
    )


def get_random_valid_building():
    while True:
        b = random.choice(ConfigBuilding.INSTANCES.values())
        if get_need_club_lv(b.id, 2) & get_need_gold(b.id, 2) & get_up_need_time(b.id, 2):
            return b


def get_need_club_lv(building_id, level):
    b_cfg = ConfigBuilding.get(building_id)
    return b_cfg.get_level(level).up_need_club_level


def get_need_gold(building_id, level):
    b_cfg = ConfigBuilding.get(building_id)
    return b_cfg.get_level(level).up_need_gold


def get_up_need_time(building_id, level):
    b_cfg = ConfigBuilding.get(building_id)
    return b_cfg.get_level(level).up_need_minutes


def get_not_exist_building():
    for i in range(1, 1000):
        if i not in ConfigBuilding.INSTANCES.keys():
            return i


class TestBuilding(object):
    def setUp(self):
        BuildingManager(1, 1)

    def tearDown(self):
        MongoBuilding.db(1).drop()

    def test_get_level(self):
        b = get_random_valid_building()
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
        b = get_random_valid_building()
        set_building_level(b.id, b.max_levels)
        try:
            BuildingManager(1, 1).level_up(b.id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("BUILDING_ALREADY_MAX_LEVEL")
        else:
            raise Exception("can not be here!")

    def test_level_up_building_upgrading(self):
        b = get_random_valid_building()
        try:
            BuildingManager(1, 1).level_up(b.id)
            BuildingManager(1, 1).level_up(b.id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("BUILDING_IN_UPGRADING")
        else:
            raise Exception('error')

    def test_level_up_club_level_not_enough(self):
        b = get_random_valid_building()
        set_building_level(b.id, b.max_levels - 1)

        MongoCharacter.db(1).update_one(
            {'_id': 1},
            {'$set': {'club.level': get_need_club_lv(b.id, b.max_levels-1) - 1}}
        )
        try:
            BuildingManager(1, 1).level_up(b.id)
        except GameException as e:
            print e.error_id
            assert e.error_id == ConfigErrorMessage.get_error_id("CLUB_LEVEL_NOT_ENOUGH")
        else:
            raise Exception("can not be here!")

    def test_level_up_gold_not_enough(self):
        b = get_random_valid_building()
        set_building_level(b.id, b.max_levels - 1)

        MongoCharacter.db(1).update_one(
            {'_id': 1},
            {'$set': {'club.level': get_need_club_lv(b.id, b.max_levels-1)}}
        )

        try:
            BuildingManager(1, 1).level_up(b.id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("GOLD_NOT_ENOUGH")
        else:
            raise Exception("can not be here!")

    def test_level_up(self):
        b = get_random_valid_building()
        set_building_level(b.id, b.max_levels - 1)

        MongoCharacter.db(1).update_one(
            {'_id': 1},
            {'$set': {
                'club.level': get_need_club_lv(b.id, b.max_levels-1),
                'club.gold': get_need_gold(b.id, b.max_levels -1),
            }}
        )

        BuildingManager(1, 1).level_up(b.id)
        data = MongoBuilding.db(1).find_one({'_id': 1}, {'buildings.{0}'.format(b.id): 1})
        assert data['buildings'][str(b.id)]['end_at'] > 0
        assert MongoCharacter.db(1).find_one({'_id': 1})['club']['gold'] == 0

    def test_levelup_callback_not_end(self):
        b = get_random_valid_building()
        BuildingManager(1, 1).level_up(b.id)
        ret = BuildingManager(1, 1).levelup_callback(b.id)
        assert ret > 0

    def test_levelup_callback(self):
        b = get_random_valid_building()
        set_building_level(b.id, 1)
        BuildingManager(1, 1).level_up(b.id)

        t = get_up_need_time(b.id, 1)
        print t
        import time
        time.sleep(t * 60)
        BuildingManager(1, 1).levelup_callback(b.id)

        data = MongoBuilding.db(1).find_one({'_id': 1}, {'buildings.{0}'.format(b.id): 1})
        assert data['buildings'][str(b.id)]['level'] == 2

