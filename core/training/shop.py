# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       shop
Date Created:   2015-11-02 10:26
Description:    网店

"""

from dianjing.exception import GameException

from core.mongo import MongoTrainingShop
from core.staff import StaffManger
from core.package import Drop
from core.mail import MailManager
from core.skill import SkillManager

from utils.message import MessagePipe

from config import ConfigErrorMessage, ConfigShop, ConfigSkill

from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE
from protomsg.training_pb2 import (
    TRAINING_SLOT_EMPTY,
    TRAINING_SLOT_NOT_OPEN,
    TRAINING_SLOT_TRAINING,

    TrainingShopNotify,
)

import formula


# 网店
class TrainingShop(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoTrainingShop.exist(self.server_id, self.char_id):
            doc = MongoTrainingShop.document()
            doc['_id'] = self.char_id

            for shop_id in ConfigShop.INSTANCES.keys():
                if ConfigShop.get(shop_id).unlock_type == 1:
                    # 无需解锁
                    doc['shops'][str(shop_id)] = 0

            MongoTrainingShop.db(self.server_id).insert_one(doc)

    def staff_is_training(self, staff_id):
        doc = MongoTrainingShop.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'shops': 1}
        )

        for v in doc['shops'].values():
            if v == staff_id:
                return True

        return False

    def trig_open_by_club_level(self, club_level):
        doc = MongoTrainingShop.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'shops': 1}
        )

        opened_shop_ids = []
        for shop_id in ConfigShop.INSTANCES.keys():
            if ConfigShop.get(shop_id).unlock_type != 2:
                continue

            if ConfigShop.get(shop_id).unlock_value > club_level:
                continue

            if str(shop_id) in doc['shops']:
                continue

            opened_shop_ids.append(shop_id)

        if opened_shop_ids:
            self.open(opened_shop_ids)

    def trig_open_by_vip_level(self, vip_level):
        doc = MongoTrainingShop.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'shops': 1}
        )

        opened_shop_ids = []
        for shop_id in ConfigShop.INSTANCES.keys():
            if ConfigShop.get(shop_id).unlock_type != 3:
                continue

            if ConfigShop.get(shop_id).unlock_value > vip_level:
                continue

            if str(shop_id) in doc['shops']:
                continue

            opened_shop_ids.append(shop_id)

        if opened_shop_ids:
            self.open(opened_shop_ids)

    def cronjob(self):
        # 每天发送邮件
        doc = MongoTrainingShop.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'shops': 1}
        )

        for shop_id, staff_id in doc['shops'].iteritems():
            if not staff_id:
                continue

            config_shop = ConfigShop.get(shop_id)
            config_skill = ConfigSkill.get(ConfigSkill.SHOP_SKILL_ID)
            shop_skill_level = SkillManager(self.server_id, self.char_id).get_staff_shop_skill_level(staff_id)
            staff = StaffManger(self.server_id, self.char_id).get_staff(staff_id)

            reward = formula.staff_training_shop_reward_gold(
                config_shop.income,
                staff.xintai,
                staff.yishi,
                config_skill.value_base,
                config_skill.level_grow,
                shop_skill_level
            )

            drop = Drop()
            drop.gold = reward
            attachment = drop.to_json()

            m = MailManager(self.server_id, self.char_id)
            m.add(config_shop.mail_title, config_shop.mail_content, attachment=attachment)

        self.send_notify()

    def open(self, shop_ids):
        updater = {'shops.{0}'.format(i): 0 for i in shop_ids}

        MongoTrainingShop.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )
        self.send_notify(shop_ids=shop_ids)

    def start(self, shop_id, staff_id):
        from core.training import TrainingExp, TrainingBroadcast

        if not StaffManger(self.server_id, self.char_id).has_staff(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        if not ConfigShop.get(shop_id):
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_SHOP_NOT_EXIST"))

        # 不能同时进行
        if TrainingExp(self.server_id, self.char_id).staff_is_training(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_DOING_EXP"))

        if TrainingBroadcast(self.server_id, self.char_id).staff_is_training(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_DOING_BROADCAST"))

        doc = MongoTrainingShop.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'shops': 1}
        )

        if str(shop_id) not in doc['shops']:
            raise GameException(ConfigErrorMessage.get_error_id("TRAINING_SHOP_NOT_OPEN"))

        for k, v in doc['shops'].iteritems():
            if v == staff_id:
                raise GameException(ConfigErrorMessage.get_error_id("TRAINING_SHOP_STAFF_IN_TRAINING"))

        MongoTrainingShop.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'shops.{0}'.format(shop_id): staff_id
            }}
        )

        self.send_notify(shop_ids=[shop_id])

    def send_notify(self, shop_ids=None):
        if shop_ids:
            act = ACT_UPDATE
            projections = {'shops.{0}'.format(i): 1 for i in shop_ids}
        else:
            act = ACT_INIT
            projections = {'shops': 1}
            shop_ids = ConfigShop.INSTANCES.keys()

        doc = MongoTrainingShop.db(self.server_id).find_one(
            {'_id': self.char_id},
            projections
        )

        notify = TrainingShopNotify()
        notify.act = act

        for i in shop_ids:
            notify_slot = notify.slots.add()
            notify_slot.id = i

            if str(i) not in doc['shops']:
                notify_slot.status = TRAINING_SLOT_NOT_OPEN
            else:
                staff_id = doc['shops'][str(i)]
                if staff_id:
                    notify_slot.status = TRAINING_SLOT_TRAINING
                    notify_slot.staff_id = staff_id
                else:
                    notify_slot.status = TRAINING_SLOT_EMPTY

        MessagePipe(self.char_id).put(msg=notify)
