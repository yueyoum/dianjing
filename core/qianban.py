# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       qianban
Date Created:   2015-08-24 11:04
Description:

"""


from config import ConfigQianBan, ConfigStaff, ConfigSkill


class QianBanEffect(object):
    __slots__ = ['effect_property', 'effect_match_skill', 'effect_business_skill']
    def __init__(self):
        # 属性效果
        self.effect_property = {}
        # 战斗技能效果
        self.effect_match_skill = {}
        # 商业技能效果
        self.effect_business_skill = {}

    def add_property(self, key, value):
        self.effect_property[key] = self.effect_property.get(key, 0) + value

    def add_skill(self, sid, value):
        if ConfigSkill.get(sid).type_id == 1:
            # 商业技能
            self.effect_business_skill[sid] = self.effect_business_skill.get(sid, 0) + value
        else:
            self.effect_match_skill[sid] = self.effect_match_skill.get(sid, 0) + value


    def __iadd__(self, other):
        """

        :type other: QianBanEffect
        """
        for k, v in other.effect_property.iteritems():
            self.effect_property[k] = self.effect_property.get(k, 0) + v

        for k, v in other.effect_match_skill.iteritems():
            self.effect_match_skill[k] = self.effect_match_skill.get(k, 0) + v

        for k, v in other.effect_business_skill.iteritems():
            self.effect_business_skill[k] = self.effect_business_skill.get(k, 0) + v

        return self



class QianBan(object):
    def __init__(self, qid, all_match_staff_ids, this_staff_skill_ids):
        self.id = qid
        self.config = ConfigQianBan.get(qid)
        self.effect = QianBanEffect()

        if self.config.condition_tp == 1:
            self.effects_for_match_staffs(all_match_staff_ids)
        else:
            self.effects_for_have_skill(this_staff_skill_ids)

    def effects_for_match_staffs(self, all_match_staff_ids):
        for i in self.config.condition_value:
            if i not in all_match_staff_ids:
                return

        self.add_to_effect()

    def effects_for_have_skill(self, this_staff_skill_ids):
        for i in self.config.condition_value:
            if i not in this_staff_skill_ids:
                return

        self.add_to_effect()

    def add_to_effect(self):
        if self.config.addition_tp == 'skill':
            for k, v in self.config.addition_skill.iteritems():
                self.effect.add_skill(k, v)
        else:
            self.effect.add_property(self.config.addition_tp, self.config.addition_property)


class QianBanContainer(object):
    def __init__(self, all_match_staff_ids):
        self.all_match_staff_ids = all_match_staff_ids


    def get_effect(self, staff_id, staff_skill_ids):
        """

        :type staff: core.abstract.AbstractStaff
        :rtype : QianBanEffect
        """
        config_staff = ConfigStaff.get(staff_id)
        qianban_ids = config_staff.qianban_ids

        effect = QianBanEffect()

        for i in qianban_ids:
            q = QianBan(i, self.all_match_staff_ids, staff_skill_ids)
            effect += q.effect

        return effect


    def affect(self, staff):
        """

        :type staff: core.abstract.AbstractStaff
        """
        effect = self.get_effect(staff.id, staff.skills.keys())

        for k, v in effect.effect_property.iteritems():
            setattr(staff, k, getattr(staff, k) + v)

        for k, v in effect.effect_match_skill.iteritems():
            if k in staff.skills:
                staff.skills[k] += v
