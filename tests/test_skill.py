# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_skill
Date Created:   2015-08-05 14:51
Description:

"""

import random

from dianjing.exception import GameException

from core.db import MongoDB
from core.skill import SkillManager
from core.staff import StaffManger

from config import ConfigStaff, ConfigErrorMessage, ConfigSkill

class TestSkillManager(object):
    def setUp(self):
        self.staff_id = random.choice(ConfigStaff.INSTANCES.keys())
        StaffManger(1, 1).add(self.staff_id)

    def tearDown(self):
        StaffManger(1, 1).remove(self.staff_id)


    def test_send_notify(self):
        SkillManager(1, 1).send_notify()


    def test_add_level(self):
        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        sid = random.choice(skills.keys())

        SkillManager(1, 1).add_level(self.staff_id, int(sid), 1)

        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        assert skills[sid]['level'] == 2


    def test_add_level_staff_not_exist(self):
        try:
            SkillManager(1, 1).add_level(9999, 9999, 10)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST")
        else:
            raise Exception("can not be here!")


    def test_add_level_skill_not_own(self):
        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        skill_ids = [int(i) for i in skills.keys()]

        def get_skill_id():
            while True:
                x = random.choice(ConfigSkill.INSTANCES.keys())
                if x not in skill_ids:
                    return x

        sid = get_skill_id()

        try:
            SkillManager(1, 1).add_level(self.staff_id, sid, 10)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("SKILL_NOT_OWN")
        else:
            raise Exception("can not be here!")


    def test_add_level_already_reach_max(self):
        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)

        sid = random.choice(skills.keys())
        sid = int(sid)

        config = ConfigSkill.get(sid)
        max_level = config.max_level

        key = "staffs.{0}.skills.{1}.level".format(self.staff_id, sid)

        MongoDB.get(1).staff.update_one(
            {'_id': 1},
            {'$set': {key: max_level}}
        )

        try:
            SkillManager(1, 1).add_level(self.staff_id, sid, 1)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("SKILL_ALREADY_MAX_LEVEL")
        else:
            raise Exception("can not be here!")

        assert SkillManager(1, 1).get_staff_skills(self.staff_id)[str(sid)]['level'] == max_level


    def test_add_level_beyond_max(self):
        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        sid = random.choice(skills.keys())
        sid = int(sid)

        config = ConfigSkill.get(sid)
        max_level = config.max_level

        key = "staffs.{0}.skills.{1}.level".format(self.staff_id, sid)

        MongoDB.get(1).staff.update_one(
            {'_id': 1},
            {'$set': {key: max_level-1}}
        )

        try:
            SkillManager(1, 1).add_level(self.staff_id, sid, 2)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("SKILL_WILL_BEYOND_MAX_LEVEL")
        else:
            raise Exception("can not be here!")

        assert SkillManager(1, 1).get_staff_skills(self.staff_id)[str(sid)]['level'] == max_level-1


    def test_add_toggle(self):
        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        sid = random.choice(skills.keys())

        SkillManager(1, 1).lock_toggle(self.staff_id, int(sid))
        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        assert skills[sid]['locked'] == 1

        SkillManager(1, 1).lock_toggle(self.staff_id, int(sid))
        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        assert skills[sid]['locked'] == 0


    def test_wash(self):
        SkillManager(1, 1).wash(self.staff_id)


    def test_wash_with_lock(self):
        skills = SkillManager(1 ,1).get_staff_skills(self.staff_id)
        sid = random.choice(skills.keys())

        SkillManager(1, 1).lock_toggle(self.staff_id, int(sid))

        SkillManager(1, 1).wash(self.staff_id)

        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        assert sid in skills
