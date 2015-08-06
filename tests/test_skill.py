# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_skill
Date Created:   2015-08-05 14:51
Description:

"""

import random

from dianjing.exception import GameException

from core.skill import SkillManager
from core.staff import StaffManger

from config import ConfigStaff, ConfigErrorMessage

class TestSkillManager(object):
    def setUp(self):
        self.staff_id = random.choice(ConfigStaff.INSTANCES.keys())
        StaffManger(1, 1).add(self.staff_id)

    def tearDown(self):
        StaffManger(1, 1).remove(self.staff_id)


    def test_send_notify(self):
        SkillManager(1, 1).send_notify()


    def test_add_level(self):
        skills = SkillManager(1, 1).get_skill(self.staff_id)
        sid = random.choice(skills.keys())

        SkillManager(1, 1).add_level(self.staff_id, int(sid), 10)

        skills = SkillManager(1, 1).get_skill(self.staff_id)
        assert skills[sid]['level'] == 11


    def test_add_level_staff_not_exist(self):
        try:
            SkillManager(1, 1).add_level(9999, 9999, 10)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST")
        else:
            raise Exception("can not be here!")

    def test_add_level_skill_not_own(self):
        try:
            SkillManager(1, 1).add_level(self.staff_id, 9999, 10)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("SKILL_NOT_OWN")
        else:
            raise Exception("can not be here!")


    def test_add_toggle(self):
        skills = SkillManager(1, 1).get_skill(self.staff_id)
        sid = random.choice(skills.keys())

        SkillManager(1, 1).lock_toggle(self.staff_id, int(sid))
        skills = SkillManager(1, 1).get_skill(self.staff_id)
        assert skills[sid]['locked'] == 1

        SkillManager(1, 1).lock_toggle(self.staff_id, int(sid))
        skills = SkillManager(1, 1).get_skill(self.staff_id)
        assert skills[sid]['locked'] == 0


    def test_wash(self):
        SkillManager(1, 1).wash(self.staff_id)


    def test_wash_with_lock(self):
        skills = SkillManager(1 ,1).get_skill(self.staff_id)
        sid = random.choice(skills.keys())

        SkillManager(1, 1).lock_toggle(self.staff_id, int(sid))

        SkillManager(1, 1).wash(self.staff_id)

        skills = SkillManager(1, 1).get_skill(self.staff_id)
        assert sid in skills
