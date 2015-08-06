# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_staff
Date Created:   2015-08-05 11:46
Description:

"""
import random

from dianjing.exception import GameException

from core.db import MongoDB
from core.staff import StaffManger, StaffRecruit
from config import ConfigErrorMessage, ConfigStaffRecruit, ConfigStaff, ConfigStaffLevel

from protomsg.staff_pb2 import RECRUIT_HOT, RECRUIT_DIAMOND, RECRUIT_GOLD, RECRUIT_NORMAL


class TestStaffRecruit(object):
    def update(self, gold=0, diamond=0):
        mongo = MongoDB.get(1)
        mongo.character.update_one(
            {'_id': 1},
            {'$set': {
                'club.gold': gold,
                'club.diamond': diamond,
            }}
        )

    def setUp(self):
        self.update()

    def tearDown(self):
        self.update()


    def test_send_notify(self):
        StaffRecruit(1, 1).send_notify()

    def test_refresh_hot(self):
        StaffRecruit(1, 1).refresh(RECRUIT_HOT)


    def test_refresh_diamond(self):
        config = ConfigStaffRecruit.get(3)
        cost_type = 'gold' if config.cost_type == 1 else 'diamond'
        cost_value = config.cost_value
        self.update(**{cost_type:cost_value})

        StaffRecruit(1, 1).refresh(RECRUIT_DIAMOND)


    def test_refresh_diamond_not_enough(self):
        config = ConfigStaffRecruit.get(3)
        error = "GOLD_NOT_ENOUGH" if config.cost_type == 1 else "DIAMOND_NOT_ENOUGH"

        try:
            StaffRecruit(1, 1).refresh(RECRUIT_DIAMOND)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id(error)
        else:
            raise Exception("can not be here!")


    def test_refresh_gold(self):
        config = ConfigStaffRecruit.get(2)
        cost_type = 'gold' if config.cost_type == 1 else 'diamond'
        cost_value = config.cost_value
        self.update(**{cost_type:cost_value})

        StaffRecruit(1, 1).refresh(RECRUIT_GOLD)


    def test_refresh_normal(self):
        config = ConfigStaffRecruit.get(1)
        cost_type = 'gold' if config.cost_type == 1 else 'diamond'
        cost_value = config.cost_value
        self.update(**{cost_type:cost_value})

        StaffRecruit(1, 1).refresh(RECRUIT_NORMAL)


    def test_refresh_error_tp(self):
        tp = 9999

        try:
            StaffRecruit(1, 1).refresh(tp)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("BAD_MESSAGE")
        else:
            raise Exception("can not be here!")


class TestStaffManager(object):
    def reset(self):
        MongoDB.get(1).staff.update_one(
            {'_id': 1},
            {'$set': {'staffs': {}}}
        )

    def setUp(self):
        self.reset()

    def tearDown(self):
        self.reset()


    def test_send_notify(self):
        StaffManger(1, 1).send_notify()

    def test_add(self):
        staff_id = random.choice(ConfigStaff.INSTANCES.keys())

        StaffManger(1, 1).add(staff_id)
        assert StaffManger(1, 1).has_staff(staff_id) is True

    def test_add_not_exist(self):
        def get_id():
            while True:
                staff_id = random.randint(1, 1000000)
                if staff_id not in ConfigStaff.INSTANCES.keys():
                    return staff_id

        staff_id = get_id()
        try:
            StaffManger(1, 1).add(staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST")
        else:
            raise Exception("can not be here!")


    def test_add_duplicate(self):
        staff_id = random.choice(ConfigStaff.INSTANCES.keys())

        StaffManger(1, 1).add(staff_id)
        assert StaffManger(1, 1).has_staff(staff_id) is True

        try:
            StaffManger(1, 1).add(staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_ALREADY_HAVE")
        else:
            raise Exception("can not be here!")


    def test_remove(self):
        staff_id = random.choice(ConfigStaff.INSTANCES.keys())

        StaffManger(1, 1).add(staff_id)
        assert StaffManger(1, 1).has_staff(staff_id) is True

        StaffManger(1, 1).remove(staff_id)
        assert StaffManger(1, 1).has_staff(staff_id) is False


    def test_remove_not_exist(self):
        try:
            StaffManger(1, 1).remove(1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST")
        else:
            raise Exception("can not be here!")


    def test_level_up(self):
        s = random.choice(ConfigStaff.INSTANCES.values())

        level = 5
        exp = 0
        for i in range(1, level):
            exp += ConfigStaffLevel.get(i).exp[s.quality]

        exp += 1

        StaffManger(1, 1).add(s.id)

        assert StaffManger(1, 1).get_staff(s.id)['level'] == 1
        assert StaffManger(1, 1).get_staff(s.id)['exp'] == 0

        StaffManger(1, 1).update(s.id, exp=exp)

        assert StaffManger(1, 1).get_staff(s.id)['level'] == level
        assert StaffManger(1, 1).get_staff(s.id)['exp'] == 1


    def test_level_up_to_max_level(self):
        def get_max_level():
            levels = ConfigStaffLevel.INSTANCES.keys()
            for lv in levels:
                if not ConfigStaffLevel.get(lv).next_level:
                    return lv

        max_level = get_max_level()

        s = random.choice(ConfigStaff.INSTANCES.values())

        exp = 0
        for i in range(1, max_level+1):
            exp += ConfigStaffLevel.get(i).exp[s.quality]

        exp += 10000

        StaffManger(1, 1).add(s.id)

        assert StaffManger(1, 1).get_staff(s.id)['level'] == 1
        assert StaffManger(1, 1).get_staff(s.id)['exp'] == 0

        StaffManger(1, 1).update(s.id, exp=exp)

        assert StaffManger(1, 1).get_staff(s.id)['level'] == max_level
        assert StaffManger(1, 1).get_staff(s.id)['exp'] == ConfigStaffLevel.get(max_level).exp[s.quality]-1
