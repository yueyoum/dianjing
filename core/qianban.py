# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       qianban
Date Created:   2015-08-24 11:04
Description:

"""

from config import ConfigQianBan, ConfigStaff, ConfigSkill


class QianBanEffect(object):
    """
    牵绊加成
    """
    __slots__ = ['effect_property', 'effect_match_skill', 'effect_business_skill']

    def __init__(self):
        # 属性效果
        self.effect_property = {}
        # 战斗技能效果
        self.effect_match_skill = {}
        # 商业技能效果
        self.effect_business_skill = {}

    def add_property(self, key, value):
        """
        牵绊属性加成
            加成属性key
            加成值 value
        """
        self.effect_property[key] = self.effect_property.get(key, 0) + value

    def add_skill(self, sid, value):
        """
        技能加成
            技能id sid
            加成值 value
        """
        if ConfigSkill.get(sid).type_id == 2:
            # 战斗技能
            self.effect_match_skill[sid] = self.effect_match_skill.get(sid, 0) + value
        else:
            self.effect_business_skill[sid] = self.effect_business_skill.get(sid, 0) + value

    def __iadd__(self, other):
        """
        重定义累加

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
    """
    牵绊系统
        员工之间产生的搭配效果的 管理和计算
    """
    def __init__(self, qid, all_match_staff_ids, this_staff_skill_ids):
        """
        初始化
            self._active        牵绊效果是否有效
            self.id             牵绊ID
            self.config         牵绊配置
            self.effect         牵绊加成实例

            self.config.condition_tp    牵绊影响类型
                1       影响出战员工      all_match_staff_ids
                非1     影响拥有技能      all_match_staff_ids
        """
        self._active = False
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
        """
        添加牵绊加成
            设置牵绊有效
            根据牵绊影响类型添加效果
        """
        self._active = True

        if self.config.addition_tp == 'skill':
            for k, v in self.config.addition_skill.iteritems():
                self.effect.add_skill(k, v)
        else:
            self.effect.add_property(self.config.addition_tp, self.config.addition_property)

    def __bool__(self):
        return self._active

    __nonzero__ = __bool__


class QianBanContainer(object):
    def __init__(self, all_match_staff_ids):
        self.all_match_staff_ids = all_match_staff_ids

    def find_active_qianbans(self, staff_id, staff_skill_ids):
        """

        :rtype : list[QianBan]
        """
        qianban_ids = ConfigStaff.get(staff_id).qianban_ids

        active_qianbans = []

        for i in qianban_ids:
            q = QianBan(i, self.all_match_staff_ids, staff_skill_ids)
            if q:
                active_qianbans.append(q)

        return active_qianbans

    def affect(self, staff):
        """

        :type staff: core.abstract.AbstractStaff
        """
        effect = QianBanEffect()

        qianbans = self.find_active_qianbans(staff.id, staff.skills.keys())

        staff.active_qianban_ids = [q.id for q in qianbans]

        for qb in qianbans:
            effect += qb.effect

        for k, v in effect.effect_property.iteritems():
            setattr(staff, k, getattr(staff, k) + v)

        for k, v in effect.effect_match_skill.iteritems():
            if k in staff.skills:
                staff.skills[k] += v
