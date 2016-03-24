# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       staff
Date Created:   2015-07-09 17:07
Description:

"""

from dianjing.exception import GameException

from core.abstract import AbstractStaff, STAFF_SECONDARY_ATTRS
from core.mongo import MongoStaff, MongoRecruit, MongoAuctionStaff
from core.resource import Resource
from core.common import CommonRecruitHot
from core.item import get_item_object, ItemManager, ItemId, ITEM_EQUIPMENT, ITEM_STAFF_CARD, BaseItem
from core.signals import recruit_staff_signal, staff_level_up_signal

from config import (
    ConfigStaff, ConfigStaffHot, ConfigStaffRecruit,
    ConfigStaffLevel, ConfigErrorMessage, ConfigStaffStatus,
    ConfigItem,
)

from utils.message import MessagePipe

from protomsg.staff_pb2 import StaffRecruitNotify, StaffNotify, StaffRemoveNotify
from protomsg.staff_pb2 import RECRUIT_DIAMOND, RECRUIT_GOLD, RECRUIT_HOT, RECRUIT_NORMAL
from protomsg.common_pb2 import ACT_INIT, ACT_UPDATE


def staff_level_up_need_exp(staff_id, current_level):
    return ConfigStaffLevel.get(current_level).exp[ConfigStaff.get(staff_id).quality]


def staff_training_exp_need_gold(staff_level):
    return staff_level * 1000


class Staff(AbstractStaff):
    __slots__ = []

    def __init__(self, server_id, char_id, _id, data):
        super(Staff, self).__init__()

        self.server_id = server_id
        self.char_id = char_id

        self.id = _id
        self.level = data['level']
        self.exp = data['exp']
        self.status = data['status']
        self.star = data.get('star', 0)
        self.unit_id = data.get('unit_id', 0)
        self.position = data.get('position', -1)

        config = ConfigStaff.get(self.id)
        self.race = config.race
        self.quality = config.quality

        for k, v in data['skills'].iteritems():
            k = int(k)
            self.skills[k] = v.pop('level')
            self.skills_detail[k] = v

        self.luoji = config.luoji
        self.minjie = config.minjie
        self.lilun = config.lilun
        self.wuxing = config.wuxing
        self.meili = config.meili

        # 知名度没有默认值，只会在游戏过程中增加
        self.zhimingdu = data.get('zhimingdu', 0)

        # 装备加成
        equipments = data.get('equips', {})
        for item_id, metadata in equipments.iteritems():
            item = get_item_object(item_id, metadata)
            """:type: core.item.Equipment"""

            self.equipments.append(item)

            self.luoji += item.luoji
            self.minjie += item.minjie
            self.lilun += item.lilun
            self.wuxing += item.wuxing
            self.meili += item.meili

        self.calculate_secondary_property()

        for item in self.equipments:
            for sp in STAFF_SECONDARY_ATTRS:
                value = getattr(self, sp) + getattr(item, sp)
                setattr(self, sp, value)

        for sp in STAFF_SECONDARY_ATTRS:
            value = getattr(self, sp) + data.get(sp, 0)
            setattr(self, sp, value)


RECRUIT_ENUM_TO_CONFIG_ID = {
    RECRUIT_NORMAL: 1,
    RECRUIT_GOLD: 2,
    RECRUIT_DIAMOND: 3,
}


class StaffRecruit(object):

    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

        doc = MongoRecruit.db(server_id).find_one({'_id': self.char_id}, {'_id': 1})
        if not doc:
            doc = MongoRecruit.document()
            doc['_id'] = self.char_id
            doc['tp'] = RECRUIT_HOT
            MongoRecruit.db(server_id).insert_one(doc)

    def get_self_refreshed_staffs(self):
        doc = MongoRecruit.db(self.server_id).find_one({'_id': self.char_id}, {'staffs': 1, 'tp': 1})
        tp = doc.get('tp', RECRUIT_HOT)
        if tp == RECRUIT_HOT:
            return []

        return doc['staffs']

    def get_hot_staffs(self):
        value = CommonRecruitHot.get(self.server_id)
        if not value:
            value = ConfigStaffHot.random_three()
            CommonRecruitHot.set(self.server_id, value)

        return value

    def refresh(self, tp):
        if tp not in [RECRUIT_HOT, RECRUIT_NORMAL, RECRUIT_GOLD, RECRUIT_DIAMOND]:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if tp == RECRUIT_HOT:
            staffs = self.get_hot_staffs()
        else:
            check = {'message': u'Recruit refresh. type {0}'.format(tp)}
            config = ConfigStaffRecruit.get(RECRUIT_ENUM_TO_CONFIG_ID[tp])
            if config.cost_type == 1:
                check['gold'] = -config.cost_value
            else:
                check['diamond'] = -config.cost_value

            doc = MongoRecruit.db(self.server_id).find_one(
                    {'_id': self.char_id},
                    {'times.{0}'.format(tp): 1}
            )

            times = doc['times'].get(str(tp), 0)
            is_first = False
            is_lucky = False
            if times == 0:
                is_first = True
            else:
                if (times + 1) % config.lucky_times == 0:
                    is_lucky = True

            with Resource(self.server_id, self.char_id).check(**check):
                result = config.get_refreshed_staffs(first=is_first, lucky=is_lucky)
                staffs = []

                for quality, amount in result:
                    staffs.extend(ConfigStaff.get_random_ids_by_condition(amount, quality=quality, can_recruit=True))

                # TODO: 更合理的方式
                if is_first and tp == RECRUIT_NORMAL:
                    staffs = staffs[:7]
                    staffs.append(11)

        MongoRecruit.db(self.server_id).update_one(
                {'_id': self.char_id},
                {
                    '$set': {
                        'tp': tp,
                        'staffs': staffs,
                        'recruited': [],
                    },
                    '$inc': {'times.{0}'.format(tp): 1}
                }
        )

        self.send_notify(staffs=staffs, tp=tp)
        return staffs

    def recruit(self, staff_id):
        if not ConfigStaff.get(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id('STAFF_NOT_EXIST'))

        doc = MongoRecruit.db(self.server_id).find_one(
                {'_id': self.char_id},
                {'recruited': 1}
        )
        recruited = doc.get('recruited', [])

        if staff_id in recruited:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if StaffManger(self.server_id, self.char_id).has_staff(staff_id):
            # raise GameException(ConfigErrorMessage.get_error_id('STAFF_ALREADY_HAVE'))
            ItemManager(self.server_id, self.char_id).add_staff_card(staff_id, 0)
        else:
            recruit_list = self.get_self_refreshed_staffs()
            if not recruit_list:
                recruit_list = self.get_hot_staffs()

            if staff_id not in recruit_list:
                raise GameException(ConfigErrorMessage.get_error_id("STAFF_RECRUIT_NOT_IN_LIST"))

            from core.building import BuildingStaffCenter
            discount = BuildingStaffCenter(self.server_id, self.char_id).recruit_discount()

            check = {"message": u"Recruit staff {0}".format(staff_id)}
            config = ConfigStaff.get(staff_id)
            if config.buy_type == 1:
                check['gold'] = -config.buy_cost * (100 + discount) / 100
            else:
                check['diamond'] = -config.buy_cost * (100 + discount) / 100

            with Resource(self.server_id, self.char_id).check(**check):
                StaffManger(self.server_id, self.char_id).add(staff_id)

        MongoRecruit.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$push': {'recruited': staff_id}}
        )

        self.send_notify()
        recruit_staff_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
                staff_id=staff_id
        )

    def send_notify(self, staffs=None, tp=None):
        if not staffs:
            staffs = self.get_self_refreshed_staffs()
            if not staffs:
                # 取common中的人气推荐
                staffs = self.get_hot_staffs()
                tp = RECRUIT_HOT
            else:
                tp = MongoRecruit.db(self.server_id).find_one({'_id': self.char_id}, {'tp': 1})['tp']

        doc = MongoRecruit.db(self.server_id).find_one(
                {'_id': self.char_id},
                {'recruited': 1}
        )
        recruited = doc.get('recruited', [])

        notify = StaffRecruitNotify()
        notify.tp = tp
        for s in staffs:
            r = notify.recruits.add()
            r.staff_id = s
            r.has_recruit = s in recruited

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
        return len(self.get_all_staffs())

    def get_all_staff_ids(self):
        return [int(i) for i in self.get_all_staffs().keys()]

    def get_all_staffs(self):
        """

        :rtype: dict[str, dict]
        """
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, {'staffs': 1})
        return doc['staffs']

    def get_staff(self, staff_id):
        """

        :rtype : Staff
        """
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, {'staffs.{0}'.format(staff_id): 1})
        data = doc['staffs'].get(str(staff_id), None)
        if not data:
            return data
        return Staff(self.server_id, self.char_id, staff_id, data)

    def get_staff_by_ids(self, ids):
        """

        :rtype : dict[int, Staff]
        """
        projection = {'staffs.{0}'.format(i): 1 for i in ids}
        doc = MongoStaff.db(self.server_id).find_one(
                {'_id': self.char_id},
                projection
        )

        staffs = {}
        for k, v in doc['staffs'].iteritems():
            staffs[int(k)] = Staff(self.server_id, self.char_id, int(k), v)

        return staffs

    def has_staff(self, staff_ids):
        if not isinstance(staff_ids, (list, tuple)):
            staff_ids = [staff_ids]

        projection = {'staffs.{0}'.format(i): 1 for i in staff_ids}
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, projection)
        if not doc:
            return False

        auc_doc = MongoAuctionStaff.db(self.server_id).find({'char_id': self.char_id}, {'staff_id': 1})
        for staff in auc_doc:
            if staff_ids == staff['staff_id']:
                return False

        staffs = doc.get('staffs', {})
        if len(staff_ids) != len(staffs.keys()):
            return False

        return True

    def add_staff(self, _id, exp, level, status, skills, send_notify=True):
        doc = MongoStaff.document_staff()
        # 员工属性
        doc['exp'] = exp
        doc['level'] = level
        doc['status'] = status
        doc['skills'] = {}
        for k, v in skills.iteritems():
            s = MongoStaff.document_staff_skill()
            s['level'] = v

            doc['skills'][str(k)] = v

        MongoStaff.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {'staffs.{0}'.format(doc['staff_id']): doc}},
        )

        if send_notify:
            self.send_notify(staff_ids=[_id])

    def add(self, staff_id, send_notify=True):
        from core.club import Club

        if not ConfigStaff.get(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        if self.has_staff(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_ALREADY_HAVE"))

        club = Club(self.server_id, self.char_id, load_staff=False)
        if self.staffs_amount >= club.max_slots_amount:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_AMOUNT_REACH_MAX_LIMIT"))

        doc = MongoStaff.document_staff()
        doc['status'] = ConfigStaffStatus.DEFAULT_STATUS
        default_skills = ConfigStaff.get(staff_id).skill_ids

        skills = {str(sid): MongoStaff.document_staff_skill() for sid in default_skills}
        doc['skills'] = skills

        MongoStaff.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {'staffs.{0}'.format(staff_id): doc}},
        )

        if send_notify:
            self.send_notify(staff_ids=[staff_id])

    def is_free(self, staff_id):
        from core.club import Club
        from core.training import TrainingShop, TrainingBroadcast, TrainingExp, TrainingProperty
        from core.skill import SkillManager

        if not self.has_staff(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        if Club(self.server_id, self.char_id).is_staff_in_match(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_CAN_NOT_REMOVE_IN_MATCH"))

        if TrainingShop(self.server_id, self.char_id).staff_is_training(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_FIRE_TRAINING_SHOP"))

        if TrainingBroadcast(self.server_id, self.char_id).staff_is_training(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_FIRE_TRAINING_BROADCAST"))

        if TrainingExp(self.server_id, self.char_id).staff_is_training(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_FIRE_TRAINING_EXP"))

        if TrainingProperty(self.server_id, self.char_id).staff_is_training(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_FIRE_TRAINING_PROPERTY"))

        if SkillManager(self.server_id, self.char_id).staff_is_training(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_FIRE_TRAINING_SKILL"))

    def remove(self, staff_id):
        self.is_free(staff_id)

        MongoStaff.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$unset': {'staffs.{0}'.format(staff_id): 1}}
        )

        notify = StaffRemoveNotify()
        notify.id.append(staff_id)
        MessagePipe(self.char_id).put(msg=notify)

    def update(self, staff_id, **kwargs):
        this_staff = self.get_staff(staff_id)
        if not this_staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        exp = kwargs.get('exp', 0)

        luoji = kwargs.get('luoji', 0)
        minjie = kwargs.get('minjie', 0)
        lilun = kwargs.get('lilun', 0)
        wuxing = kwargs.get('wuxing', 0)
        meili = kwargs.get('meili', 0)

        zhimingdu = kwargs.get('zhimingdu', 0)

        # update
        level_updated = False
        current_level = this_staff.level
        current_exp = this_staff.exp + exp
        if exp > 0:
            while True:
                need_exp = staff_level_up_need_exp(staff_id, current_level)

                next_level = ConfigStaffLevel.get(current_level).next_level
                if not next_level:
                    if current_exp >= need_exp:
                        current_exp = need_exp - 1
                    break

                if current_exp < need_exp:
                    break

                current_exp -= need_exp
                current_level += 1
                level_updated = True

        MongoStaff.db(self.server_id).update_one(
                {'_id': self.char_id},
                {
                    '$set': {
                        'staffs.{0}.exp'.format(staff_id): current_exp,
                        'staffs.{0}.level'.format(staff_id): current_level
                    },

                    '$inc': {
                        'staffs.{0}.luoji'.format(staff_id): luoji,
                        'staffs.{0}.minjie'.format(staff_id): minjie,
                        'staffs.{0}.lilun'.format(staff_id): lilun,
                        'staffs.{0}.wuxing'.format(staff_id): wuxing,
                        'staffs.{0}.meili'.format(staff_id): meili,

                        'staffs.{0}.zhimingdu'.format(staff_id): zhimingdu,
                    },
                }
        )

        if level_updated:
            staff_level_up_signal.send(
                    sender=None,
                    server_id=self.server_id,
                    char_id=self.char_id,
                    staff_id=staff_id,
                    new_level=current_level
            )

        self.send_notify(staff_ids=[staff_id])

    def equipment_on(self, staff_id, item_id):
        if not self.has_staff(staff_id):
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        id_object = ItemId.parse(item_id)

        config = ConfigItem.get(id_object.oid)
        if not config:
            raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        if config.tp != ITEM_EQUIPMENT:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_EQUIP_ON_TYPE_ERROR"))

        metadata = BaseItem.get_metadata(self.server_id, self.char_id, item_id)
        if not metadata:
            raise GameException(ConfigErrorMessage.get_error_id("ITEM_NOT_EXIST"))

        im = ItemManager(self.server_id, self.char_id)
        im.remove_by_item_id(item_id)

        doc = MongoStaff.db(self.server_id).find_one(
                {'_id': self.char_id},
                {'staffs.{0}.equips'.format(staff_id): 1}
        )

        updater = {
            '$set': {
                'staffs.{0}.equips.{1}'.format(staff_id, item_id): metadata
            }
        }

        for item_id in doc.get('equips', {}):
            id_object = ItemId.parse(item_id)
            if ConfigItem.get(id_object.oid).group_id == config.group_id:
                # 同类型的替换
                updater['$unset'] = {
                    'staffs.{0}.equips.{1}'.format(staff_id, item_id): 1
                }
                break

        MongoStaff.db(self.server_id).update_one(
                {'_id': self.char_id},
                updater
        )

        self.send_notify(staff_ids=[staff_id])

    def strengthen(self, staff_id):
        staff = self.get_staff(staff_id)
        if not staff:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_NOT_EXIST"))

        im = ItemManager(self.server_id, self.char_id)
        items = im.get_all_items()

        find_item_id = ""
        for item in items:
            if item.id_object.type_id == ITEM_STAFF_CARD and item.id_object.star == staff.star:
                find_item_id = item.id_object.id
                break

        if not find_item_id:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_STRENGTH_NO_CARD"))

        im.remove_by_item_id(find_item_id)

        # TODO max star
        MongoStaff.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$inc': {
                    'staffs.{0}.star'.format(staff_id): 1
                }}
        )

        self.send_notify(staff_ids=[staff_id])

    def update_winning_rate(self, results, one=True):
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, {'staffs': 1})
        staff_ids = [int(i) for i in doc.get('staffs', {}).keys()]

        updater = {}
        for result in results:
            # 员工是否还在
            if result.staff_one not in staff_ids:
                continue

            if one:
                # 挑战者
                race_two = ConfigStaff.get(result.staff_two).race
                updater['staffs.{0}.winning_rate.{1}.total'.format(result.staff_one, race_two)] = 1
                if result.staff_one_win:
                    updater['staffs.{0}.winning_rate.{1}.win'.format(result.staff_one, race_two)] = 1
            else:
                # 被挑战者
                race_one = ConfigStaff.get(result.staff_one).race
                updater['staffs.{0}.winning_rate.{1}.total'.format(result.staff_two, race_one)] = 1
                if not result.staff_one_win:
                    updater['staffs.{0}.winning_rate.{1}.win'.format(result.staff_two, race_one)] = 1

        MongoStaff.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$inc': updater}
        )

    def get_winning_rate(self, staff_ids):
        projection = {'staffs.{0}.winning_rate'.format(staff_id): 1 for staff_id in staff_ids}
        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, projection)
        return doc['staffs']

    def send_notify(self, staff_ids=None):
        if not staff_ids:
            projection = {'staffs': 1}
            act = ACT_INIT
        else:
            projection = {'staffs.{0}'.format(i): 1 for i in staff_ids}
            act = ACT_UPDATE

        doc = MongoStaff.db(self.server_id).find_one({'_id': self.char_id}, projection)
        staffs = doc.get('staffs', {})

        notify = StaffNotify()
        notify.act = act
        for k, v in staffs.iteritems():
            notify_staff = notify.staffs.add()
            staff = Staff(self.server_id, self.char_id, int(k), v)
            notify_staff.MergeFrom(staff.make_protomsg())

        MessagePipe(self.char_id).put(msg=notify)
