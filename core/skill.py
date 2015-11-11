# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       skill
Date Created:   2015-07-24 10:34
Description:

"""

import random
import arrow

from dianjing.exception import GameException

from core.mongo import MongoStaff
from core.bag import BagTrainingSkill
from core.resource import Resource

from utils.message import MessagePipe
from utils.api import Timerd

from protomsg.skill_pb2 import SkillNotify
from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT

from config import ConfigStaff, ConfigSkill, ConfigErrorMessage, ConfigTrainingSkillItem, ConfigSkillWashCost

TIMER_UPGRADE_PATH = "/api/timerd/skill"


class SkillManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def get_staff_skills(self, staff_id):
        key = "staffs.{0}.skills".format(staff_id)
        doc = MongoStaff.db(self.server_id).find_one(
            {'_id': self.char_id},
            {key: 1}
        )
        if not doc or str(staff_id) not in doc['staffs']:
            return None

        return doc['staffs'][str(staff_id)]['skills']

    def get_staff_skill_level(self, staff_id, skill_id):
        skills = self.get_staff_skills(staff_id)
        if skills and skills.get(str(skill_id), None):
            return skills[str(skill_id)]['level']
        else:
            return 0

    def get_staff_shop_skill_level(self, staff_id):
        return self.get_staff_skill_level(staff_id, ConfigSkill.SHOP_SKILL_ID)

    def get_staff_broadcast_skill_level(self, staff_id):
        return self.get_staff_skill_level(staff_id, ConfigSkill.BROADCAST_SKILL_ID)

    def get_staff_sponsor_skill_level(self, staff_id):
        return self.get_staff_skill_level(staff_id, ConfigSkill.SPONSOR_SKILL_ID)

    def check(self, staff_id, skill_id=None):
        from core.staff import StaffManger

        if not StaffManger(self.server_id, self.char_id).has_staff(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        if skill_id:
            if not ConfigSkill.get(skill_id):
                raise GameException(ConfigErrorMessage.get_error_id("SKILL_NOT_EXISTS"))

            doc = MongoStaff.db(self.server_id).find_one(
                {'_id': self.char_id},
                {'staffs.{0}.skills.{1}'.format(staff_id, skill_id): 1}
            )

            try:
                this_skill = doc['staffs'][str(staff_id)]['skills'][str(skill_id)]
            except KeyError:
                raise GameException(ConfigErrorMessage.get_error_id("SKILL_NOT_OWN"))
            else:
                return this_skill

        return None

    def upgrade(self, staff_id, skill_id):
        this_skill = self.check(staff_id, skill_id)
        if this_skill.get('end_at', 0):
            raise GameException(ConfigErrorMessage.get_error_id("SKILL_ALREADY_IN_UPGRADE"))

        config = ConfigSkill.get(skill_id)
        level = this_skill['level']
        if level >= config.max_level:
            raise GameException(ConfigErrorMessage.get_error_id("SKILL_ALREADY_MAX_LEVEL"))

        need_id, need_amount = config.get_upgrade_needs(level)

        with BagTrainingSkill(self.server_id, self.char_id).remove_context(need_id, need_amount):
            value = arrow.utcnow().timestamp + ConfigTrainingSkillItem.get(need_id).minutes * 60

            data = {
                'sid': self.server_id,
                'cid': self.char_id,
                'staff_id': staff_id,
                'skill_id': skill_id,
            }

            key = Timerd.register(value, TIMER_UPGRADE_PATH, data)

            MongoStaff.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    "staffs.{0}.skills.{1}.end_at".format(staff_id, skill_id): value,
                    "staffs.{0}.skills.{1}.key".format(staff_id, skill_id): key,
                }}
            )

        self.send_notify(act=ACT_UPDATE, staff_id=staff_id, skill_id=skill_id)

    def upgrade_speedup(self, staff_id, skill_id):
        this_skill = self.check(staff_id, skill_id)
        end_at = this_skill.get('end_at', 0)
        if not end_at:
            raise GameException(ConfigErrorMessage.get_error_id("SKILL_UPGRADE_SPEEDUP_CANNOT"))

        behind_seconds = end_at - arrow.utcnow().timestamp
        if behind_seconds <= 0:
            self.update(skill_id, skill_id)
        else:
            minutes, seconds = divmod(behind_seconds, 60)
            if seconds:
                minutes += 1

            need_diamond = minutes * 10
            message = u"Skill Upgrade SpeedUp"

            with Resource(self.server_id, self.char_id).check(diamond=-need_diamond, message=message):
                self.update(staff_id, skill_id)

        if this_skill['key']:
            Timerd.cancel(this_skill['key'])

    def lock_toggle(self, staff_id, skill_id):
        self.check(staff_id, skill_id)
        key = "staffs.{0}.skills.{1}.locked".format(staff_id, skill_id)

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$bit': {key: {'xor': 1}}}
        )

        self.send_notify(act=ACT_UPDATE, staff_id=staff_id, skill_id=skill_id)

    def wash(self, staff_id):
        self.check(staff_id)

        skills = self.get_staff_skills(staff_id)

        wash_skills = {}
        new_skills = {}
        for k, v in skills.iteritems():
            if v['locked'] == 1:
                new_skills[k] = v
            else:
                wash_skills[k] = v

        locked_skill_amount = len(new_skills)

        race = ConfigStaff.get(staff_id).race
        race_skills = ConfigSkill.filter(race=race)
        race_skill_ids = race_skills.keys()

        while len(new_skills) < 4:
            if not race_skill_ids:
                break

            picked_skill = random.choice(race_skill_ids)
            race_skill_ids.remove(picked_skill)

            if str(picked_skill) not in new_skills:
                new_skills[str(picked_skill)] = MongoStaff.document_staff_skill()

        if len(new_skills) < 4:
            raise RuntimeError("Not enough skills for race {0}".format(race))

        cost = ConfigSkillWashCost.get_cost(locked_skill_amount)
        cost['message'] = u"Skill Wash. locked amount {0}".format(locked_skill_amount)

        with Resource(self.server_id, self.char_id).check(**cost):
            MongoStaff.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {"staffs.{0}.skills".format(staff_id): new_skills}}
            )

            for k, v in wash_skills.iteritems():
                if v['key']:
                    Timerd.cancel(v['key'])

        self.send_notify()

    def send_notify(self, act=ACT_INIT, staff_id=None, skill_id=None):
        # 这个必须在 StaffNotify 之后
        # 这里的 act 必须手动指定，因为添加新员工后，这里的sill notify 得是 ACT_INIT
        if not staff_id:
            projection = {'staffs': 1}
        else:
            if not skill_id:
                projection = {'staffs.{0}.skills'.format(staff_id): 1}
            else:
                projection = {'staffs.{0}.skills.{1}'.format(staff_id, skill_id): 1}

        doc = MongoStaff.db(self.server_id).find_one(
            {'_id': self.char_id},
            projection
        )

        notify = SkillNotify()
        notify.act = act

        for k, v in doc['staffs'].iteritems():
            notify_staff = notify.staff_skills.add()
            notify_staff.staff_id = int(k)

            for sid, sinfo in v['skills'].iteritems():
                notify_staff_skill = notify_staff.skills.add()
                notify_staff_skill.id = int(sid)
                notify_staff_skill.level = sinfo['level']
                notify_staff_skill.locked = sinfo['locked'] == 1
                notify_staff_skill.upgrade_end_at = sinfo.get('end_at', 0)

        MessagePipe(self.char_id).put(msg=notify)

    def update(self, staff_id, skill_id):
        level = "staffs.{0}.skills.{1}.level".format(staff_id, skill_id)
        end_at = "staffs.{0}.skills.{1}.end_at".format(staff_id, skill_id)
        key = "staffs.{0}.skills.{1}.key".format(staff_id, skill_id)

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {
                '$inc': {level: 1},
                '$set': {end_at: 0, key: ''},
            }
        )

        self.send_notify(act=ACT_UPDATE, staff_id=staff_id, skill_id=skill_id)

    def timer_callback(self, staff_id, skill_id):
        data = self.get_staff_skills(staff_id)
        if 0 < data[str(skill_id)]['end_at'] <= arrow.utcnow().timestamp:
            self.update(staff_id, skill_id)
        else:
            return data[str(skill_id)]['end_at']

        return 0



