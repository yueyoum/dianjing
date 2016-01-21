# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       skill
Date Created:   2015-07-24 10:34
Description:    相关文档见 电竞经理/俱乐部设施/培训中心

"""

import random
import arrow

from dianjing.exception import GameException

from core.mongo import MongoStaff
from core.item import ItemManager
from core.resource import Resource
from core.staff import StaffManger

from utils.api import Timerd

from config import ConfigStaff, ConfigSkill, ConfigErrorMessage, ConfigSkillWashCost

import formula

TIMER_CALLBACK_PATH = "/api/timerd/skill/"


class SkillManager(object):
    """
    技能管理系统
        员工技能管理
    """
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def staff_is_training(self, staff_id):
        """
            返回员工是否正在技能训练
            是, 返回 True
            不是, 返回 False
        """
        skills = self.get_staff_skills(staff_id)
        if not skills:
            return False

        for v in skills.values():
            if v.get('end_at', 0):
                return True

        return False

    def get_staff_skills(self, staff_id):
        """
            如果 玩家 拥有 该员工, 返回员工技能list
            否则，返回None
        """
        key = "staffs.{0}.skills".format(staff_id)
        doc = MongoStaff.db(self.server_id).find_one(
            {'_id': self.char_id},
            {key: 1}
        )
        if not doc or str(staff_id) not in doc['staffs']:
            return None

        return doc['staffs'][str(staff_id)]['skills']

    def get_staff_skill_level(self, staff_id, skill_id):
        """
            如果员工拥有该技能， 返回该技能等级
            否则，返回0
        """
        skills = self.get_staff_skills(staff_id)
        if skills and skills.get(str(skill_id), None):
            return int(skills[str(skill_id)]['level'])
        else:
            return 0

    def get_staff_shop_skill_level(self, staff_id):
        """
        返回员工 网店 技能等级
        """
        return self.get_staff_skill_level(staff_id, ConfigSkill.SHOP_SKILL_ID)

    def get_staff_broadcast_skill_level(self, staff_id):
        """
        返回员工 直播 技能等级
        """
        return self.get_staff_skill_level(staff_id, ConfigSkill.BROADCAST_SKILL_ID)

    def get_staff_sponsor_skill_level(self, staff_id):
        """
        返回员工 赞助 技能等级
        """
        return self.get_staff_skill_level(staff_id, ConfigSkill.SPONSOR_SKILL_ID)

    def check(self, staff_id, skill_id=None):
        """
        检查员工是否存在, 且是否拥有某技能
            拥有, 则返回技能属性
            否则, 返回None

            1 检测是否拥有该员工
            2 检查技能是否存在
            3 检查 该员工 是否拥有 该技能
            4 返回结果(拥有 返回技能; 没有, 返回 None)
        """
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
        """
        升级技能
            1 检测升级条件
                1.1 正在升级技能不能重复升级
                1.2 满级技能不能升级
                1.3 消耗品不足不能升级
            2 设置技能为升级状态
            3 同步技能信息到客户端
        """
        this_skill = self.check(staff_id, skill_id)
        if this_skill.get('end_at', 0):
            raise GameException(ConfigErrorMessage.get_error_id("SKILL_ALREADY_IN_UPGRADE"))

        config = ConfigSkill.get(skill_id)
        level = this_skill['level']
        if level >= config.max_level:
            raise GameException(ConfigErrorMessage.get_error_id("SKILL_ALREADY_MAX_LEVEL"))

        level_info = config.levels[str(level)]
        minutes = level_info['minutes']
        needs = level_info['upgrade_items']

        im = ItemManager(self.server_id, self.char_id)
        im.check_exists(needs, is_oid=True)

        end_at = arrow.utcnow().timestamp + minutes * 60
        data = {
            'sid': self.server_id,
            'cid': self.char_id,
            'staff_id': staff_id,
            'skill_id': skill_id,
        }

        key = Timerd.register(end_at, TIMER_CALLBACK_PATH, data)

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                "staffs.{0}.skills.{1}.end_at".format(staff_id, skill_id): end_at,
                "staffs.{0}.skills.{1}.key".format(staff_id, skill_id): key,
            }}
        )

        im.remove_items_by_oid(needs)
        self.send_notify(staff_id)

    def upgrade_speedup(self, staff_id, skill_id):
        """
        技能升级加速,立即完成技能升级
            1 检查技能升级是否已经完成
            2 计算加速消耗
            3 检查消耗是否足够
            4 扣除消耗, 立刻完成技能升级
            5 取消升级定时任务
        """
        this_skill = self.check(staff_id, skill_id)
        end_at = this_skill.get('end_at', 0)
        if not end_at:
            raise GameException(ConfigErrorMessage.get_error_id("SKILL_UPGRADE_SPEEDUP_CANNOT"))

        behind_seconds = end_at - arrow.utcnow().timestamp
        need_diamond = formula.training_speedup_need_diamond(behind_seconds)
        if need_diamond == 0:
            self.update(staff_id, skill_id)
        else:
            message = u"Skill Upgrade SpeedUp, staff_id: {0}, skill_id: {1}".format(staff_id, skill_id)

            with Resource(self.server_id, self.char_id).check(diamond=-need_diamond, message=message):
                self.update(staff_id, skill_id)

        if this_skill['key']:
            Timerd.cancel(this_skill['key'])

    def lock_toggle(self, staff_id, skill_id):
        """
            技能加锁/解锁
            加锁技能不会被洗练
        """
        self.check(staff_id, skill_id)
        key = "staffs.{0}.skills.{1}.locked".format(staff_id, skill_id)

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$bit': {key: {'xor': 1}}}
        )

        self.send_notify(staff_id)

    def wash(self, staff_id):
        """
        技能洗练
            传入一个员工ID(int)
            获取未锁定技能wash_skills(locked != 1)
            计算资源消耗并检测资源是否足够
            获得员工可学习技能race_skill_ids(剔除掉已学习的技能--加锁技能槽技能)
            添加技能到new_skill
            写入MongoStaff
            通知客户端员工技能
        """
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
        cost = ConfigSkillWashCost.get_cost(locked_skill_amount)
        cost['message'] = u"Skill Wash. locked amount {0}".format(locked_skill_amount)

        with Resource(self.server_id, self.char_id).check(**cost):
            race = ConfigStaff.get(staff_id).race
            race_skills = ConfigSkill.filter(race=race)
            race_skill_ids = [i for i in (set(race_skills.keys()) - set(new_skills))]

            while len(new_skills) < 4:
                if not race_skill_ids:
                    break

                picked_skill = random.choice(race_skill_ids)
                race_skill_ids.remove(picked_skill)

                if str(picked_skill) not in new_skills:
                    new_skills[str(picked_skill)] = MongoStaff.document_staff_skill()

            if len(new_skills) < 4:
                raise RuntimeError("Not enough skills for race {0}".format(race))

            MongoStaff.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {"staffs.{0}.skills".format(staff_id): new_skills}}
            )

            for k, v in wash_skills.iteritems():
                key = v.get('key', '')
                if key:
                    Timerd.cancel(key)

        self.send_notify(staff_id)

    def send_notify(self, staff_id):
        """
            同步员工技能信息
        """
        # 这个必须在 StaffNotify 之后
        # 这里的 act 必须手动指定，因为添加新员工后，这里的skill notify 得是 ACT_INIT
        StaffManger(self.server_id, self.char_id).send_notify(staff_ids=[staff_id])


    def update(self, staff_id, skill_id):
        """
            1, 将升级技能更新到MongoStaff
            2, 同步技能信息到客户端
        """
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

        self.send_notify(staff_id)

    def timer_callback(self, staff_id, skill_id):
        """
        技能升级 timer 回调
        """
        self.update(staff_id, skill_id)
