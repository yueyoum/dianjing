# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       skill
Date Created:   2015-07-24 10:34
Description:

"""

import random

from core.db import get_mongo_db
from core.mongo import Document

from utils.message import MessagePipe

from protomsg.skill_pb2 import SkillNotify
from protomsg.common_pb2 import ACT_UPDATE, ACT_INIT

from config import ConfigStaff, ConfigSkill


class SkillManager(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        self.mongo = get_mongo_db(server_id)


    def lock_toggle(self, staff_id, skill_id):
        # TODO check staff, skill exists?

        key = "staffs.{0}.skills.{1}.locked".format(staff_id, skill_id)

        self.mongo.character.update_one(
            {'_id': self.char_id},
            {'$bit': {key: {'xor': 1}}}
        )

        self.send_notify(act=ACT_UPDATE, staff_id=staff_id, skill_id=skill_id)


    def wash(self, staff_id):
        # TODO check

        char = self.mongo.character.find_one(
            {'_id': self.char_id},
            {'staffs.{0}.skills'.format(staff_id): 1}
        )

        skills = char['staffs'][str(staff_id)]['skills']
        new_skills = {}
        for k, v in skills.iteritems():
            if v['locked'] == 1:
                new_skills[k] = v


        race = ConfigStaff.get(staff_id).race
        race_skills = ConfigSkill.filter(race=race)
        race_skill_ids = race_skills.keys()

        while len(new_skills) < 4:
            # TODO ...
            picked_skill = random.choice(race_skill_ids)
            race_skill_ids.remove(picked_skill)

            if str(picked_skill) not in new_skills:
                new_skills[str(picked_skill)] = Document.get("skill")


        self.mongo.character.update_one(
            {'_id': self.char_id},
            {'$set': {"staffs.{0}.skills".format(staff_id): new_skills}}
        )

        self.send_notify()


    def send_notify(self, act=ACT_INIT, staff_id=None, skill_id=None):
        # 这个必须在 StaffNotify 之后

        if not staff_id:
            projection = {'staffs': 1}
        else:
            if not skill_id:
                projection = {'staffs.{0}.skills'.format(staff_id): 1}
            else:
                projection = {'staffs.{0}.skills.{1}'.format(staff_id, skill_id): 1}

        char = self.mongo.character.find_one(
            {'_id': self.char_id},
            projection
        )

        notify = SkillNotify()
        notify.act = act

        for k, v in char['staffs'].iteritems():
            notify_staff = notify.staff_skills.add()
            notify_staff.staff_id = int(k)

            for sid, sinfo in v['skills'].iteritems():
                notify_staff_skill = notify_staff.skills.add()
                notify_staff_skill.id = int(sid)
                notify_staff_skill.level = sinfo['level']
                notify_staff_skill.locked = sinfo['locked'] == 1

        MessagePipe(self.char_id).put(msg=notify)





