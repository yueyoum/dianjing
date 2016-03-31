# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_staff
Date Created:   2015-08-05 11:46
Description:

"""
import random

from dianjing.exception import GameException

from core.mongo import MongoCharacter, MongoRecruit, MongoStaff
from core.staff import StaffManger, StaffRecruit, RECRUIT_ENUM_TO_CONFIG_ID
from core.club import Club
from config import ConfigErrorMessage, ConfigStaffRecruit, ConfigStaff, ConfigStaffLevel

from protomsg.staff_pb2 import RECRUIT_HOT, RECRUIT_DIAMOND, RECRUIT_GOLD, RECRUIT_NORMAL


class TestStaffRecruit(object):
    def __init__(self):
        self.server_id = 1
        self.char_id = 1

    def update(self, gold=0, diamond=0):
        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'club.gold': gold,
                'club.diamond': diamond,
            }}
        )

    def setup(self):
        self.update()

    def teardown(self):
        self.update()
        MongoRecruit.db(1).delete_one({'_id': self.char_id})

    def test_send_notify(self):
        StaffRecruit(self.server_id, self.char_id).send_notify()

    def test_refresh_hot(self):
        StaffRecruit(self.server_id, self.char_id).refresh(RECRUIT_HOT)

    def test_refresh_normal(self):
        config = ConfigStaffRecruit.get(RECRUIT_ENUM_TO_CONFIG_ID[RECRUIT_NORMAL])
        for i in range(1, config.lucky_times+1):
            self.update(**{'gold': config.cost_value})
            StaffRecruit(self.server_id, self.char_id).refresh(RECRUIT_NORMAL)
            staff_ids = StaffRecruit(self.server_id, self.char_id).get_self_refreshed_staffs()

            quality_s = 0
            quality_a = 0
            quality_b = 0
            quality_c = 0
            for staff_id in staff_ids:
                conf = ConfigStaff.get(int(staff_id))
                if conf.quality == 'S':
                    quality_s += 1
                elif conf.quality == 'A':
                    quality_a += 1
                elif conf.quality == 'B':
                    quality_b += 1
                elif conf.quality == 'C':
                    quality_c += 1

            if i == 1:
                assert quality_s == 1
                assert quality_a == 1
                assert quality_b == 2
                assert quality_c == 4
            elif i % config.lucky_times == 0:
                assert quality_a == 1
                assert quality_b == 2
                assert quality_c == 5
            else:
                assert quality_b == 2
                assert quality_c == 6

    def test_refresh_gold(self):
        config = ConfigStaffRecruit.get(RECRUIT_ENUM_TO_CONFIG_ID[RECRUIT_GOLD])
        for i in range(1, config.lucky_times+1):
            self.update(**{'diamond': config.cost_value})
            StaffRecruit(self.server_id, self.char_id).refresh(RECRUIT_GOLD)
            staff_ids = StaffRecruit(self.server_id, self.char_id).get_self_refreshed_staffs()

            quality_s = 0
            quality_a = 0
            quality_b = 0
            for staff_id in staff_ids:
                conf = ConfigStaff.get(int(staff_id))
                if conf.quality == 'S':
                    quality_s += 1
                elif conf.quality == 'A':
                    quality_a += 1
                elif conf.quality == 'B':
                    quality_b += 1

            if i == 1 or i % config.lucky_times == 0:
                assert quality_s == 1
                assert quality_a == 1
                assert quality_b == 6

            else:
                assert quality_a == 2
                assert quality_b == 6

    def test_refresh_diamond(self):
        config = ConfigStaffRecruit.get(RECRUIT_ENUM_TO_CONFIG_ID[RECRUIT_DIAMOND])
        for i in range(1, config.lucky_times+1):
            self.update(**{'diamond': config.cost_value})
            StaffRecruit(self.server_id, self.char_id).refresh(RECRUIT_DIAMOND)
            staff_ids = StaffRecruit(self.server_id, self.char_id).get_self_refreshed_staffs()

            quality_ss = 0
            quality_s = 0
            quality_a = 0
            for staff_id in staff_ids:
                conf = ConfigStaff.get(int(staff_id))
                if conf.quality == 'SS':
                    quality_ss += 1
                elif conf.quality == 'S':
                    quality_s += 1
                elif conf.quality == 'A':
                    quality_a += 1

            if i ==1 or i % config.lucky_times == 0:
                assert quality_ss == 1
                assert quality_s == 1
                assert quality_a == 6

            else:
                assert quality_s == 2
                assert quality_a == 6

    def test_refresh_by_use_resource(self):
        config = ConfigStaffRecruit.get(random.choice(ConfigStaffRecruit.INSTANCES.keys()))
        cost_type = 'gold' if config.cost_type == 1 else 'diamond'
        self.update(**{cost_type: config.cost_value})

        tp = RECRUIT_NORMAL
        if config.cost_type == 2:
            tp = RECRUIT_GOLD
        if config.cost_type == 3:
            tp = RECRUIT_DIAMOND

        staffs = StaffRecruit(self.server_id, self.char_id).refresh(tp)
        assert len(staffs) > 0

    def test_refresh_resource_not_enough(self):
        config = ConfigStaffRecruit.get(random.choice(ConfigStaffRecruit.INSTANCES.keys()))
        error = "GOLD_NOT_ENOUGH" if config.cost_type == 1 else "DIAMOND_NOT_ENOUGH"
        tp = RECRUIT_DIAMOND if config.cost_type == 2 else RECRUIT_NORMAL

        try:
            StaffRecruit(self.server_id, self.char_id).refresh(tp)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id(error)
        else:
            raise Exception("can not be here!")

    def test_refresh_error_tp(self):
        tp = 9999
        try:
            StaffRecruit(self.server_id, self.char_id).refresh(tp)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("BAD_MESSAGE")
        else:
            raise Exception("can not be here!")

    def test_recruit_staff_not_exist(self):
        staff_ids = ConfigStaff.INSTANCES.keys()
        test_id = 0
        for i in range(0, 10000):
            if i not in staff_ids:
                test_id = i
                break
        try:
            StaffRecruit(self.server_id, self.char_id).recruit(test_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST")
        else:
            raise Exception("error")

    def test_recruit_not_in_list(self):
        config = ConfigStaffRecruit.get(RECRUIT_ENUM_TO_CONFIG_ID[RECRUIT_NORMAL])
        cost_type = 'gold' if config.cost_type == 1 else 'diamond'
        self.update(**{cost_type: config.cost_value})
        StaffRecruit(self.server_id, self.char_id).refresh(RECRUIT_NORMAL)

        config_ids = ConfigStaff.INSTANCES.keys()
        staff_ids = StaffRecruit(self.server_id, self.char_id).get_self_refreshed_staffs()
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, {'staffs': 1})
        has_staffs = [int(staff_id) for staff_id in doc['staffs'].keys()]

        staffs_set = set(staff_ids) | set(has_staffs)
        test_id = 0
        for staff_id in config_ids:
            if staff_id not in staffs_set:
                test_id = staff_id
                break
        try:
            StaffRecruit(self.server_id, self.char_id).recruit(test_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_RECRUIT_NOT_IN_LIST")
        else:
            raise Exception("can not be here!")

    def test_recruit_already_have(self):
        config = ConfigStaffRecruit.get(RECRUIT_ENUM_TO_CONFIG_ID[RECRUIT_NORMAL])
        cost_type = 'gold' if config.cost_type == 1 else 'diamond'
        self.update(**{cost_type: config.cost_value})
        StaffRecruit(self.server_id, self.char_id).refresh(RECRUIT_NORMAL)

        staff_ids = StaffRecruit(self.server_id, self.char_id).get_self_refreshed_staffs()
        doc = MongoStaff.db(self.server_id).find_one({'_id': 1}, {'staffs': 1})
        test_id = 0
        for staff_id in staff_ids:
            if str(staff_id) not in doc['staffs'].keys():
                StaffManger(self.server_id, self.char_id).add(staff_id)
                test_id = staff_id
                break
        try:
            StaffRecruit(self.server_id, self.char_id).recruit(test_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_ALREADY_HAVE")
        else:
            raise Exception("can not be here!")

    def test_recruit(self):
        config = ConfigStaffRecruit.get(RECRUIT_ENUM_TO_CONFIG_ID[RECRUIT_NORMAL])
        cost_type = 'gold' if config.cost_type == 1 else 'diamond'
        self.update(**{cost_type: config.cost_value})
        StaffRecruit(self.server_id, self.char_id).refresh(RECRUIT_NORMAL)

        staff_ids = StaffRecruit(self.server_id, self.char_id).get_self_refreshed_staffs()
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, {'staffs': 1})
        test_id = 0
        for staff_id in staff_ids:
            if str(staff_id) not in doc['staffs'].keys():
                test_id = staff_id
                break

        assert StaffManger(self.server_id, self.char_id).has_staff(test_id) is False
        staff_cfg = ConfigStaff.get(test_id)
        tp = 'gold' if staff_cfg.buy_type == 1 else 'diamond'
        self.update(**{tp: staff_cfg.buy_cost})
        StaffRecruit(self.server_id, self.char_id).recruit(test_id)
        assert StaffManger(self.server_id, self.char_id).has_staff(test_id) is True


class TestStaffManager(object):
    def __init__(self):
        self.server_id = 1
        self.char_id = 1

    def setup(self):
        StaffManger(self.server_id, self.char_id)

    def teardown(self):
        MongoStaff.db(self.server_id).delete_one({'_id': self.char_id})

    def test_send_notify(self):
        StaffManger(self.server_id, self.char_id).send_notify()

    def test_add(self):
        staff_ids = ConfigStaff.INSTANCES.keys()
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, {'staffs': 1})

        add_id = 0
        for staff_id in staff_ids:
            if str(staff_id) not in doc['staffs'].keys():
                add_id = staff_id

        StaffManger(self.server_id, self.char_id).add(add_id)
        assert StaffManger(self.server_id, self.char_id).has_staff(add_id) is True

    def test_add_not_exist(self):
        def get_id():
            while True:
                staff_id = random.randint(1, 1000000)
                if staff_id not in ConfigStaff.INSTANCES.keys():
                    return staff_id

        staff_id = get_id()
        try:
            StaffManger(self.server_id, self.char_id).add(staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST")
        else:
            raise Exception("can not be here!")

    def test_add_duplicate(self):
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, {'staffs': 1})
        staff_id = int(random.choice(doc['staffs'].keys()))

        assert StaffManger(self.server_id, self.char_id).has_staff(staff_id) is True
        try:
            StaffManger(self.server_id, self.char_id).add(staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_ALREADY_HAVE")
        else:
            raise Exception("can not be here!")

    def test_remove(self):
        staff_ids = ConfigStaff.INSTANCES.keys()
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id})
        staff_id = 0
        for i in staff_ids:
            if str(i) not in doc['staffs'].keys():
                staff_id = i
                break

        StaffManger(self.server_id, self.char_id).add(staff_id)
        assert StaffManger(self.server_id, self.char_id).has_staff(staff_id) is True

        StaffManger(self.server_id, self.char_id).remove(staff_id)
        assert StaffManger(self.server_id, self.char_id).has_staff(staff_id) is False

    def test_remove_not_exist(self):
        staff_ids = ConfigStaff.INSTANCES.keys()

        staff_id = 0
        for i in range(1, 10000):
            if str(i) not in staff_ids:
                staff_id = i
                break
        try:
            StaffManger(self.server_id, self.char_id).remove(staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST")
        else:
            raise Exception("can not be here!")

    def test_level_up(self):
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, {'staffs': 1})
        s = ConfigStaff.get(int(random.choice(doc['staffs'].keys())))

        level = 5
        exp = 0
        for i in range(1, level):
            exp += ConfigStaffLevel.get(i).exp[s.quality]

        exp += 1

        assert StaffManger(self.server_id, self.char_id).get_staff_object(s.id).level == 1
        assert StaffManger(self.server_id, self.char_id).get_staff_object(s.id).exp == 0

        StaffManger(self.server_id, self.char_id).update(s.id, exp=exp)
        assert StaffManger(self.server_id, self.char_id).get_staff_object(s.id).level == level
        assert StaffManger(self.server_id, self.char_id).get_staff_object(s.id).exp == 1

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
        StaffManger(self.server_id, self.char_id).add(s.id)

        assert StaffManger(self.server_id, self.char_id).get_staff_object(s.id).level == 1
        assert StaffManger(self.server_id, self.char_id).get_staff_object(s.id).exp == 0

        StaffManger(self.server_id, self.char_id).update(s.id, exp=exp)
        assert StaffManger(self.server_id, self.char_id).get_staff_object(s.id).level == max_level
        assert StaffManger(self.server_id, self.char_id).get_staff_object(s.id).exp == ConfigStaffLevel.get(max_level).exp[s.quality] - 1

