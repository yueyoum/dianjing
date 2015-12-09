# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       test_skill
Date Created:   2015-08-05 14:51
Description:

"""

import random
import arrow

from dianjing.exception import GameException

from core.mongo import MongoStaff, MongoCharacter
from core.skill import SkillManager
from core.staff import StaffManger
from core.bag import BagTrainingSkill

from config import ConfigStaff, ConfigErrorMessage, ConfigSkill, ConfigSkillWashCost


class TestSkillManager(object):
    def setup(self):
        self.staff_id = random.choice(ConfigStaff.INSTANCES.keys())
        if not StaffManger(1, 1).has_staff(self.staff_id):
            StaffManger(1, 1).add(self.staff_id)

    def teardown(self):
        if StaffManger(1, 1).has_staff(self.staff_id):
            if not SkillManager(1, 1).staff_is_training(self.staff_id):
                StaffManger(1, 1).remove(self.staff_id)

    def test_send_notify(self):
        SkillManager(1, 1).send_notify()
        SkillManager(1, 1).send_notify(staff_id=self.staff_id)

    def test_get_staff_skills(self):
        assert SkillManager(1, 1).get_staff_skills(self.staff_id)

    def test_get_staff_skill_level(self):
        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        skill_id = random.choice(skills.keys())
        assert SkillManager(1, 1).get_staff_skill_level(self.staff_id, skill_id)

    def test_check_staff_not_exist(self):
        staffs = MongoStaff.db(1).find_one({'_id': 1}, {'staffs': 1})
        staff_ids = staffs['staffs'].keys()

        staff_id = 0
        for i in range(1000, 1111):
            if str(i) not in staff_ids:
                staff_id = i
                break
        try:
            SkillManager(1, 1).check(staff_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST")
        else:
            raise Exception('Error')

    def test_check_skill_not_exist(self):
        skill_id = 0
        for i in range(1111, 22222):
            if i not in ConfigSkill.INSTANCES.keys():
                skill_id = i
        try:
            SkillManager(1, 1).check(self.staff_id, skill_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("SKILL_NOT_EXISTS")
        else:
            raise Exception('error')

    def test_check_skill_not_own(self):
        skill_id = 0
        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        for i in ConfigSkill.INSTANCES.keys():
            if i not in skills.keys():
                skill_id = i

        try:
            SkillManager(1, 1).check(self.staff_id, skill_id)
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("SKILL_NOT_OWN")
        else:
            raise Exception('error')

    def test_check(self):
        assert not SkillManager(1, 1).check(self.staff_id)

        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        skill_id = random.choice(skills.keys())
        assert SkillManager(1, 1).check(self.staff_id, int(skill_id))

    def test_upgrade_upgrading(self):
        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        skill_id = random.choice(skills.keys())

        MongoStaff.db(1).update_one(
            {'_id': 1},
            {"$set":
                {'staffs.{0}.skills.{1}.end_at'.format(self.staff_id, skill_id): arrow.utcnow().timestamp + 10}}
        )

        try:
            SkillManager(1, 1).upgrade(self.staff_id, int(skill_id))
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("SKILL_ALREADY_IN_UPGRADE")
        else:
            raise Exception('error')

    def test_upgrade_already_max_level(self):
        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        skill_id = random.choice(skills.keys())
        config = ConfigSkill.get(int(skill_id))

        MongoStaff.db(1).update_one(
            {'_id': 1},
            {"$set":
                {'staffs.{0}.skills.{1}.level'.format(self.staff_id, skill_id): config.max_level}}
        )

        try:
            SkillManager(1, 1).upgrade(self.staff_id, int(skill_id))
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("SKILL_ALREADY_MAX_LEVEL")
        else:
            raise Exception('error')

    def test_upgrade(self):
        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        skill_id = random.choice(skills.keys())
        config = ConfigSkill.get(int(skill_id))

        need_id, need_amount = config.get_upgrade_needs(skills[str(skill_id)]['level']+1)
        BagTrainingSkill(1, 1).add([(need_id, need_amount)])

        SkillManager(1, 1).upgrade(self.staff_id, int(skill_id))
        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        assert skills[str(skill_id)]['end_at'] > 0

    def test_upgrade_speedup_can_not(self):
        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        skill_id = random.choice(skills.keys())
        try:
            SkillManager(1, 1).upgrade_speedup(self.staff_id, int(skill_id))
        except GameException as e:
            assert e.error_id == ConfigErrorMessage.get_error_id("SKILL_UPGRADE_SPEEDUP_CANNOT")
        else:
            raise Exception('error')

    def test_upgrade_speedup(self):
        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        skill_id = random.choice(skills.keys())
        config = ConfigSkill.get(int(skill_id))

        need_id, need_amount = config.get_upgrade_needs(skills[str(skill_id)]['level']+1)
        BagTrainingSkill(1, 1).add([(need_id, need_amount)])

        MongoCharacter.db(1).update_one(
            {'_id': 1},
            {'$set': {'club.diamond': 10000}}
        )

        SkillManager(1, 1).upgrade(self.staff_id, int(skill_id))
        SkillManager(1, 1).upgrade_speedup(self.staff_id, int(skill_id))

        skills_after = SkillManager(1, 1).get_staff_skills(self.staff_id)
        assert skills_after[str(skill_id)]['level'] == skills[str(skill_id)]['level']+1

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
        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        new_skills = {}
        for k, v in skills.iteritems():
            if v['locked'] == 1:
                new_skills[k] = v

        cost = ConfigSkillWashCost.get_cost(len(new_skills))
        if cost.get('gold', 0):
            key = 'club.gold'
            span = cost['gold']
        else:
            key = 'club.diamond'
            span = cost['diamond']

        MongoCharacter.db(1).update_one(
            {'_id': 1},
            {'$set': {key: -span}}
        )

        SkillManager(1, 1).wash(self.staff_id)

        club = MongoCharacter.db(1).find_one(
            {'_id': 1},
            {'club': 1}
        )

        if key == 'club.diamond':
            assert club['club']['diamond'] == 0
        else:
            assert club['club']['gold'] == 0

    def test_wash_with_lock(self):
        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        sid = random.choice(skills.keys())

        SkillManager(1, 1).lock_toggle(self.staff_id, int(sid))
        cost = ConfigSkillWashCost.get_cost(1)
        MongoCharacter.db(1).update_one(
            {'_id': 1},
            {'$set': {'club.diamond': cost}}
        )

        SkillManager(1, 1).wash(self.staff_id)

        skills = SkillManager(1, 1).get_staff_skills(self.staff_id)
        assert sid in skills
