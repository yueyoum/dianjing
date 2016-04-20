# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       staff
Date Created:   2015-07-09 17:07
Description:

"""

import random

from dianjing.exception import GameException

from core.abstract import AbstractStaff
from core.mongo import MongoStaff, MongoRecruit
from core.resource import money_text_to_item_id, ResourceClassification
from core.common import CommonRecruitHot
from core.bag import Bag, TYPE_EQUIPMENT, get_item_type
from core.signals import recruit_staff_signal, staff_level_up_signal

from config import (
    ConfigStaffHot, ConfigStaffRecruit,
    ConfigErrorMessage,
    ConfigItemNew,
    ConfigStaffNew,
    ConfigStaffStar,
    ConfigStaffLevelNew,
    ConfigItemExp,
    ConfigEquipmentNew,
)

from utils.functional import make_string_id
from utils.message import MessagePipe

from protomsg.bag_pb2 import EQUIP_DECORATION, EQUIP_KEYBOARD, EQUIP_MONITOR, EQUIP_MOUSE
from protomsg.staff_pb2 import StaffRecruitNotify, StaffNotify, StaffRemoveNotify
from protomsg.staff_pb2 import RECRUIT_DIAMOND, RECRUIT_GOLD, RECRUIT_HOT, RECRUIT_NORMAL
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE

#
# RECRUIT_ENUM_TO_CONFIG_ID = {
#     RECRUIT_NORMAL: 1,
#     RECRUIT_GOLD: 2,
#     RECRUIT_DIAMOND: 3,
# }
#
#
# class StaffRecruit(object):
#     def __init__(self, server_id, char_id):
#         self.server_id = server_id
#         self.char_id = char_id
#
#         doc = MongoRecruit.db(server_id).find_one({'_id': self.char_id}, {'_id': 1})
#         if not doc:
#             doc = MongoRecruit.document()
#             doc['_id'] = self.char_id
#             doc['tp'] = RECRUIT_HOT
#             MongoRecruit.db(server_id).insert_one(doc)
#
#     def get_self_refreshed_staffs(self):
#         doc = MongoRecruit.db(self.server_id).find_one({'_id': self.char_id}, {'staffs': 1, 'tp': 1})
#         tp = doc.get('tp', RECRUIT_HOT)
#         if tp == RECRUIT_HOT:
#             return []
#
#         return doc['staffs']
#
#     def get_hot_staffs(self):
#         value = CommonRecruitHot.get(self.server_id)
#         if not value:
#             value = ConfigStaffHot.random_three()
#             CommonRecruitHot.set(self.server_id, value)
#
#         return value
#
#     def refresh(self, tp):
#         if tp not in [RECRUIT_HOT, RECRUIT_NORMAL, RECRUIT_GOLD, RECRUIT_DIAMOND]:
#             raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))
#
#         if tp == RECRUIT_HOT:
#             staffs = self.get_hot_staffs()
#         else:
#             check = {'message': u'Recruit refresh. type {0}'.format(tp)}
#             config = ConfigStaffRecruit.get(RECRUIT_ENUM_TO_CONFIG_ID[tp])
#             if config.cost_type == 1:
#                 check['gold'] = -config.cost_value
#             else:
#                 check['diamond'] = -config.cost_value
#
#             doc = MongoRecruit.db(self.server_id).find_one(
#                 {'_id': self.char_id},
#                 {'times.{0}'.format(tp): 1}
#             )
#
#             times = doc['times'].get(str(tp), 0)
#             is_first = False
#             is_lucky = False
#             if times == 0:
#                 is_first = True
#             else:
#                 if (times + 1) % config.lucky_times == 0:
#                     is_lucky = True
#
#             with Resource(self.server_id, self.char_id).check(**check):
#                 result = config.get_refreshed_staffs(first=is_first, lucky=is_lucky)
#                 staffs = []
#
#                 for quality, amount in result:
#                     staffs.extend(ConfigStaff.get_random_ids_by_condition(amount, quality=quality, can_recruit=True))
#
#                 # TODO: 更合理的方式
#                 if is_first and tp == RECRUIT_NORMAL:
#                     staffs = staffs[:7]
#                     staffs.append(11)
#
#         MongoRecruit.db(self.server_id).update_one(
#             {'_id': self.char_id},
#             {
#                 '$set': {
#                     'tp': tp,
#                     'staffs': staffs,
#                     'recruited': [],
#                 },
#                 '$inc': {'times.{0}'.format(tp): 1}
#             }
#         )
#
#         self.send_notify(staffs=staffs, tp=tp)
#         return staffs
#
#     def recruit(self, staff_id):
#         if not ConfigStaff.get(staff_id):
#             raise GameException(ConfigErrorMessage.get_error_id('STAFF_NOT_EXIST'))
#
#         doc = MongoRecruit.db(self.server_id).find_one(
#             {'_id': self.char_id},
#             {'recruited': 1}
#         )
#         recruited = doc.get('recruited', [])
#
#         if staff_id in recruited:
#             raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))
#
#         if StaffManger(self.server_id, self.char_id).has_staff(staff_id):
#             # raise GameException(ConfigErrorMessage.get_error_id('STAFF_ALREADY_HAVE'))
#             ItemManager(self.server_id, self.char_id).add_staff_card(staff_id, 0)
#         else:
#             recruit_list = self.get_self_refreshed_staffs()
#             if not recruit_list:
#                 recruit_list = self.get_hot_staffs()
#
#             if staff_id not in recruit_list:
#                 raise GameException(ConfigErrorMessage.get_error_id("STAFF_RECRUIT_NOT_IN_LIST"))
#
#             from core.building import BuildingStaffCenter
#             discount = BuildingStaffCenter(self.server_id, self.char_id).recruit_discount()
#
#             check = {"message": u"Recruit staff {0}".format(staff_id)}
#             config = ConfigStaff.get(staff_id)
#             if config.buy_type == 1:
#                 check['gold'] = -config.buy_cost * (100 + discount) / 100
#             else:
#                 check['diamond'] = -config.buy_cost * (100 + discount) / 100
#
#             with Resource(self.server_id, self.char_id).check(**check):
#                 StaffManger(self.server_id, self.char_id).add(staff_id)
#
#         MongoRecruit.db(self.server_id).update_one(
#             {'_id': self.char_id},
#             {'$push': {'recruited': staff_id}}
#         )
#
#         self.send_notify()
#         recruit_staff_signal.send(
#             sender=None,
#             server_id=self.server_id,
#             char_id=self.char_id,
#             staff_id=staff_id
#         )
#
#     def send_notify(self, staffs=None, tp=None):
#         if not staffs:
#             staffs = self.get_self_refreshed_staffs()
#             if not staffs:
#                 # 取common中的人气推荐
#                 staffs = self.get_hot_staffs()
#                 tp = RECRUIT_HOT
#             else:
#                 tp = MongoRecruit.db(self.server_id).find_one({'_id': self.char_id}, {'tp': 1})['tp']
#
#         doc = MongoRecruit.db(self.server_id).find_one(
#             {'_id': self.char_id},
#             {'recruited': 1}
#         )
#         recruited = doc.get('recruited', [])
#
#         notify = StaffRecruitNotify()
#         notify.tp = tp
#         for s in staffs:
#             r = notify.recruits.add()
#             r.staff_id = s
#             r.has_recruit = s in recruited
#
#         MessagePipe(self.char_id).put(msg=notify)


###################################
STAFF_MAX_LEVEL = max(ConfigStaffNew.INSTANCES.keys())
STAFF_MAX_STAR = max(ConfigStaffStar.INSTANCES.keys())


class Staff(AbstractStaff):
    __slots__ = []

    def __init__(self, server_id, char_id, unique_id, data):
        super(Staff, self).__init__()

        self.server_id = server_id
        self.char_id = char_id

        self.id = unique_id
        self.oid = data['oid']
        self.level = data['level']
        self.step = data['step']
        self.star = data['star']
        self.level_exp = data['level_exp']
        self.star_exp = data['star_exp']

        self.equip_mouse = data['equip_mouse']
        self.equip_keyboard = data['equip_keyboard']
        self.equip_monitor = data['equip_monitor']
        self.equip_decoration = data['equip_decoration']

        self.after_init()


    def level_up(self, using_items):
        # using_items: [(id, amount)...]
        # TODO 发来的物品能提供的经验可能超过了等级上限
        # 这时候只扣除升级到上限所需的物品
        if self.level >= STAFF_MAX_LEVEL:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_ALREADY_MAX_LEVEL"))

        bag = Bag(self.server_id, self.char_id)
        bag.check_items(using_items)

        increase_level_exp = 0
        for _id, _amount in using_items:
            _config = ConfigItemExp.get(_id)
            if not _config:
                raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

            increase_level_exp += _config.exp * _amount

        for _id, _amount in using_items:
            bag.remove_by_item_id(_id, _amount)

        exp = self.level_exp + increase_level_exp
        while True:
            if self.level == STAFF_MAX_LEVEL:
                if exp >= ConfigStaffLevelNew.get(self.level).exp:
                    exp = ConfigStaffLevelNew.get(self.level).exp - 1

                break

            if exp < ConfigStaffLevelNew.get(self.level).exp:
                break

            exp -= ConfigStaffLevelNew.get(self.level).exp
            self.level += 1

        self.level_exp = exp

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'set': {
                'staffs.{0}.level'.format(self.id): self.level,
                'staffs.{0}.level_exp'.format(self.id): self.level_exp
            }}
        )

        self.calculate()
        self.make_cache()
        self.send_notify()

    def step_up(self):
        if self.step >= self.config.max_step:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_ALREADY_MAX_STEP"))

        if self.level < self.config.steps[self.step].level_limit:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_LEVEL_NOT_ENOUGH"))

        using_items = self.config.steps[self.step].update_item_need
        resource_classified = ResourceClassification.classify(using_items)
        resource_classified.check_exist(self.server_id, self.char_id)
        resource_classified.remove(self.server_id, self.char_id)

        self.step += 1
        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': {
                'staffs.{0}.step'.format(self.id): 1
            }}
        )

        # NOTE 升阶可能会导致 天赋技能 改变
        # 不仅会影响自己，可能（如果在阵型中）也会影响到其他选手
        # 所以这里不自己 calculate， 而是先让 club 重新 load staffs

    def star_up(self):
        if self.star >= STAFF_MAX_STAR:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_ALREADY_MAX_STAR"))

        star_config = ConfigStaffStar.get(self.star)
        using_items = [(star_config.need_item_id, star_config.need_item_amount)]

        resource_classified = ResourceClassification.classify(using_items)
        resource_classified.check_exist(self.server_id, self.char_id)
        resource_classified.remove(self.server_id, self.char_id)

        if random.randint(1, 100) <= 30:
            inc_exp = 6
        else:
            inc_exp = random.randint(1, 3)

        exp = self.star_exp + inc_exp
        while True:
            if self.star == STAFF_MAX_STAR:
                if exp >= ConfigStaffStar.get(self.star).exp:
                    exp = ConfigStaffStar.get(self.star).exp - 1

                break

            if exp < ConfigStaffStar.get(self.star).exp:
                break

            exp -= ConfigStaffStar.get(self.star).exp
            self.star += 1

        self.star_exp = exp

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'staffs.{0}.star'.format(self.id): self.star,
                'staffs.{0}.star_exp'.format(self.id): self.star_exp
            }}
        )

        self.calculate()
        self.make_cache()
        self.send_notify()

    def equipment_change(self, bag_slot_id, tp):
        if not bag_slot_id:
            # 卸下
            bag_slot_id = ""
        else:
            # 更换
            bag = Bag(self.server_id, self.char_id)
            slot = bag.get_slot(bag_slot_id)

            # TODO error handle
            item_id = slot['item_id']
            if get_item_type(item_id) != TYPE_EQUIPMENT:
                raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

            equip_config = ConfigEquipmentNew.get(item_id)
            if equip_config.tp != tp:
                raise GameException(ConfigErrorMessage.get_error_id("EQUIPMENT_TYPE_NOT_MATCH"))

            if StaffManger(self.server_id, self.char_id).find_staff_id_by_equipment_slot_id(bag_slot_id):
                raise GameException(ConfigErrorMessage.get_error_id("EQUIPMENT_ON_OTHER_STUFF"))

        if tp == EQUIP_MOUSE:
            key = 'equip_mouse'
        elif tp == EQUIP_KEYBOARD:
            key = 'equip_keyboard'
        elif tp == EQUIP_MONITOR:
            key = 'equip_monitor'
        else:
            key = 'equip_decoration'

        setattr(self, key, bag_slot_id)
        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'staffs.{0}.{1}'.format(self.id, key): bag_slot_id
            }}
        )

        self.calculate()
        self.make_cache()
        self.send_notify()

    def send_notify(self):
        notify = StaffNotify()
        notify.act = ACT_UPDATE
        notify_staff = notify.staffs.add()
        notify_staff.MergeFrom(self.make_protomsg())
        MessagePipe(self.char_id).put(msg=notify)


class StaffManger(object):
    __slots__ = ['server_id', 'char_id']

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        if not MongoStaff.exist(self.server_id, self.char_id):
            doc = MongoStaff.document()
            doc['_id'] = self.char_id
            MongoStaff.db(server_id).insert_one(doc)

    @property
    def staffs_amount(self):
        # type: () -> int
        return len(self.get_staffs_data())

    def get_staffs_data(self, ids=None):
        """

        :rtype: dict[str, dict]
        """
        if ids:
            projection = {'staffs.{0}'.format(i) for i in ids}
        else:
            projection = {'staffs': 1}

        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, projection)
        return doc['staffs']

    def get_all_staff_object(self):
        # type: () -> dict[str, Staff]
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, {'staffs': 1})
        return {k: self.get_staff_object(k) for k, _ in doc['staffs'].iteritems()}

    def get_staff_object(self, _id):
        """

        :param _id:
        :rtype : Staff | None
        """
        from core.club import Club

        obj = Staff.get(_id)
        if obj:
            return obj

        Club(self.server_id, self.char_id).load_staffs()
        return Staff.get(_id)


    def has_staff(self, ids):
        # type: (list[str]) -> bool
        # unique id
        projection = {'staffs.{0}'.format(i): 1 for i in ids}
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, projection)
        if not doc:
            return False

        staffs = doc.get('staffs', {})
        return len(ids) == len(staffs)

    def check_staff(self, ids):
        if not self.has_staff(ids):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

    def check_original_staff_is_initial_state(self, originals):
        # 原始ID， 并且匹配原始属性
        # originals: [(oid, amount)...]
        oids = []
        for _oid, _amount in originals:
            oids.extend([_oid] * _amount)

        staffs = self.get_all_staff_object().values()
        """:type: list[Staff]"""
        for s in staffs:
            for i in oids:
                if s.oid == i and s.is_initial_state():
                    oids.remove(i)
                    break

        if oids:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

    def add(self, staff_original_id, send_notify=True):
        from core.club import Club

        if not ConfigStaffNew.get(staff_original_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        # club = Club(self.server_id, self.char_id, load_staff=False)
        # if self.staffs_amount >= club.max_slots_amount:
        #     raise GameException(ConfigErrorMessage.get_error_id("STAFF_AMOUNT_REACH_MAX_LIMIT"))

        unique_id = make_string_id()
        doc = MongoStaff.document_staff()
        doc['oid'] = staff_original_id

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'staffs.{0}'.format(unique_id): doc}},
        )

        if send_notify:
            self.send_notify(ids=[unique_id])

        return unique_id

    def remove(self, staff_id):

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$unset': {'staffs.{0}'.format(staff_id): 1}}
        )

        notify = StaffRemoveNotify()
        notify.ids.append(staff_id)
        MessagePipe(self.char_id).put(msg=notify)

    def remove_initial_state_staff(self, oid):
        staffs = self.get_all_staff_object().values()
        """:type: list[Staff]"""
        for s in staffs:
            if s.oid == oid and s.is_initial_state():
                self.remove(s.id)
                return

    def find_staff_id_by_equipment_slot_id(self, slot_id):
        # type: (str) -> str|None
        # 找slot_id在哪个角色身上
        assert slot_id, "Invalid slot_id: {0}".format(slot_id)
        doc = MongoStaff.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'staffs': 1}
        )

        for k, v in doc['staffs'].iteritems():
            if v['equip_mouse'] == slot_id or \
                            v['equip_keyboard'] == slot_id or \
                            v['equip_monitor'] == slot_id or \
                            v['equip_decoration'] == slot_id:
                return k

        return None

    def equipment_change(self, staff_id, slot_id, tp):
        if tp not in [EQUIP_MOUSE, EQUIP_KEYBOARD, EQUIP_MONITOR, EQUIP_DECORATION]:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        staff = self.get_staff_object(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        staff.equipment_change(slot_id, tp)

    def level_up(self, staff_id, items):
        staff = self.get_staff_object(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        staff.level_up(items)

    def step_up(self, staff_id):
        from core.club import Club
        from core.formation import Formation
        staff = self.get_staff_object(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        staff.step_up()
        in_formation_staff_ids = Formation(self.server_id, self.char_id).in_formation_staffs().keys()
        if staff.id in in_formation_staff_ids:
            Club(self.server_id, self.char_id).load_staffs()
            self.send_notify(ids=in_formation_staff_ids)
        else:
            staff.calculate()
            staff.make_cache()
            staff.send_notify()


    def star_up(self, staff_id):
        staff = self.get_staff_object(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        staff.star_up()

    def destroy(self, staff_id):
        # TODO 返还
        self.remove(staff_id)
        doc = MongoStaff.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'staffs.{0}.oid'.format(staff_id): 1}
        )

        oid = doc['staffs'][staff_id]['oid']
        crystal = ConfigStaffNew.get(oid).crystal

        drop = [(money_text_to_item_id('crystal'), crystal)]
        return drop

    def send_notify(self, ids=None):
        if not ids:
            projection = {'staffs': 1}
            act = ACT_INIT
        else:
            projection = {'staffs.{0}'.format(i): 1 for i in ids}
            act = ACT_UPDATE

        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, projection)
        staffs = doc.get('staffs', {})

        notify = StaffNotify()
        notify.act = act
        for k, _ in staffs.iteritems():
            notify_staff = notify.staffs.add()
            staff = self.get_staff_object(k)
            notify_staff.MergeFrom(staff.make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)
