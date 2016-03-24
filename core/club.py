# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       club
Date Created:   2015-07-03 15:09
Description:

"""

import random
import base64
import dill

from core.mongo import MongoCharacter, MongoStaff
from core.abstract import AbstractClub
from core.signals import match_staffs_set_done_signal, club_level_up_signal, match_staffs_set_change_signal
from core.staff import StaffManger
from core.resource import Resource
from core.statistics import FinanceStatistics

from dianjing.exception import GameException

from utils.message import MessagePipe

from config import (
    ConfigClubLevel,
    ConfigPolicy,
    ConfigErrorMessage
)

from config.settings import BUY_STAFF_SLOT_COST

from protomsg.club_pb2 import ClubNotify, ClubStaffSlotsAmountNotify


def club_level_up_need_renown(level):
    return ConfigClubLevel.get(level).renown


class Club(AbstractClub):
    __slots__ = [
        'server_id', 'char_id', 'buy_slots'
    ]

    def __init__(self, server_id, char_id, load_staff=True):
        super(Club, self).__init__()

        self.server_id = server_id
        self.char_id = char_id

        doc = MongoCharacter.db(self.server_id).find_one({'_id': self.char_id}, {'club': 1, 'name': 1, 'buy_slots': 1})
        club = doc['club']

        self.id = self.char_id  # 玩家ID
        self.name = club['name']  # 俱乐部名
        self.manager_name = doc['name']  # 角色名
        self.flag = club['flag']  # 俱乐部旗帜
        self.level = club['level']  # 俱乐部等级
        self.renown = club['renown']  # 俱乐部声望
        self.vip = club['vip']  # vip等级
        self.gold = club['gold']  # 游戏币
        self.diamond = club['diamond']  # 钻石

        self.crystal = club.get('crystal', 0)
        self.gas = club.get('gas', 0)
        self.policy = club.get('policy', 1)  # 战术

        self.match_staffs = club.get('match_staffs', [])  # 出战员工
        # self.tibu_staffs = club.get('tibu_staffs', [])  # 替补员工

        self.buy_slots = doc.get('buy_slots', 0)

        if load_staff:
            self.load_match_staffs()

    def check_money(self, diamond=0, gold=0, renown=0, crystal=0, gas=0):
        # TODO 其他货币
        if diamond > self.diamond:
            raise GameException(ConfigErrorMessage.get_error_id("DIAMOND_NOT_ENOUGH"))
        if gold > self.gold:
            raise GameException(ConfigErrorMessage.get_error_id("GOLD_NOT_ENOUGH"))
        if crystal > self.crystal:
            raise GameException(ConfigErrorMessage.get_error_id("CRYSTAL_NOT_ENOUGH"))
        if gas > self.gas:
            raise GameException(ConfigErrorMessage.get_error_id("GAS_NOT_ENOUGH"))


    # 这些 current_* 接口是给 编辑器使用的
    # 比如需要俱乐部等级的任务 里面只要填写 core.club.Club.current_level
    # 那么代码就可以找到对应需要的值
    def current_level(self):
        return self.level

    def current_vip(self):
        return self.vip

    @property
    def max_slots_amount(self):
        config = ConfigClubLevel.get(self.level)
        return config.max_staff_amount + self.buy_slots

    def load_match_staffs(self):
        all_match_staff_ids = self.all_match_staffs()
        if not all_match_staff_ids:
            return

        self.staffs = StaffManger(self.server_id, self.char_id).get_staff_by_ids(all_match_staff_ids)
        self.qianban_affect()

    def is_staff_in_match(self, staff_id):
        # return staff_id in self.match_staffs or staff_id in self.tibu_staffs
        return staff_id in self.match_staffs

    def set_policy(self, policy):
        if not ConfigPolicy.get(policy):
            raise GameException(ConfigErrorMessage.get_error_id('POLICY_NOT_EXIST'))

        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'club.policy': policy}}
        )

        self.policy = policy
        self.send_notify()

    # TODO 这个不再要呢？
    def set_match_staffs(self, staff_ids, trig_signal=True):
        # if len(staff_ids) != 6:
        #     raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        sm = StaffManger(self.server_id, self.char_id)

        # if not sm.has_staff([i for i in staff_ids if i != 0]):
        if not sm.has_staff(staff_ids):
            raise GameException(ConfigErrorMessage.get_error_id('STAFF_NOT_EXIST'))

        # match_staffs = staff_ids[:5]
        # tibu_staffs = staff_ids[5:]

        all_staffs = sm.get_all_staffs()

        old_match_staff_ids = self.match_staffs
        in_staff_ids = set(staff_ids) - set(old_match_staff_ids)
        out_staff_ids = set(staff_ids) - set(old_match_staff_ids)
        keep_staff_ids = set(staff_ids) & set(old_match_staff_ids)

        # in 的设置位置
        # out 的清除位置
        # keep 的不变

        kept_positions = [all_staffs[str(i)]['position'] for i in keep_staff_ids]

        in_positions = {}
        for i in in_staff_ids:
            while True:
                pos = random.randint(0, 29)
                if pos not in kept_positions:
                    in_positions[i] = pos
                    break

        updater = {
            'staffs.{0}.position'.format(i): 0 for i in out_staff_ids
        }

        updater.update({
            'staffs.{0}.position'.format(k): v for k, v in in_positions.iteritems()
        })

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        Club(self.server_id, self.char_id).send_notify()

        if trig_signal and staff_ids != old_match_staff_ids:
            match_staffs_set_change_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
            )

        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'club.match_staffs': staff_ids,
                # 'club.tibu_staffs': tibu_staffs
            }}
        )

        self.match_staffs = staff_ids
        # self.tibu_staffs = tibu_staffs
        self.load_match_staffs()

        # if trig_signal and all([i != 0 for i in staff_ids]):
        if trig_signal and staff_ids:
            # set done
            match_staffs_set_done_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
                match_staffs=staff_ids
            )

        self.send_notify()

    def set_unit(self, index, staff_id, unit_id):
        # if not StaffManger(self.server_id, self.char_id).has_staff(staff_id):
        #     raise GameException(ConfigErrorMessage.get_error_id('STAFF_NOT_EXIST'))

        assert index >=0 and index <= 5

        all_staffs = StaffManger(self.server_id, self.char_id).get_all_staffs()
        positions = []
        for v in all_staffs.values():
            _pos = v.get('position', 0)
            if _pos:
                positions.append(_pos)

        updater = {}

        if staff_id == 0:
            # 设置兵种. 如果本来没有位置， 就设定位置
            staff_id = self.match_staffs[index]
            assert staff_id != 0

            updater['staffs.{0}.unit_id'.format(staff_id)] = unit_id

            pos = all_staffs[str(staff_id)].get('position', 0)
            if not pos:
                while True:
                    pos = random.randint(0, 29)
                    if pos not in positions:
                        updater['staffs.{0}.position'.format(staff_id)] = pos
                        break

            # TODO 检测unit是否存在， 与staff种族是否匹配
        else:
            # 设置员工
            unit_id = 0
            MongoCharacter.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$set': {
                    'club.match_staffs.{0}'.format(index): staff_id
                }}
            )

            old_staff_id = self.match_staffs[index]
            assert old_staff_id != 0
            pos = all_staffs[str(staff_id)].get('position', 0)
            if not pos:
                while True:
                    pos = random.randint(0, 29)
                    if pos not in positions:
                        break

            # 撤下的队员 位置清除
            updater['staffs.{0}.position'.format(old_staff_id)] = 0
            # 设置新上场的
            updater['staffs.{0}.position'.format(staff_id)] = pos


        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        # self.load_match_staffs()
        # self.send_notify()
        Club(self.server_id, self.char_id).send_notify()

    def set_formation(self, info):
        # info: [(staff_id, position),...]
        doc = MongoStaff.db(self.server_id).find_one(
            {'_id': self.char_id},
            {'staffs': 1}
        )

        for staff_id, position in info:
            if position < 0 or position > 29:
                raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

            if staff_id not in self.match_staffs:
                # TODO error code
                raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

            this_staff = doc['staffs'][str(staff_id)]
            if not this_staff.get('unit_id', 0):
                raise GameException(ConfigErrorMessage.get_error_id("INVALID_OPERATE"))

        updater = {}
        for staff_id, position in info:
            updater['staffs.{0}.position'.format(staff_id)] = position

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': updater}
        )

        # self.load_match_staffs()
        # self.send_notify()
        Club(self.server_id, self.char_id).send_notify()

    def update(self, **kwargs):
        renown = kwargs.get('renown', 0)
        gold = kwargs.get('gold', 0)
        diamond = kwargs.get('diamond', 0)
        crystal = kwargs.get('crystal', 0)
        gas = kwargs.get('gas', 0)
        message = kwargs.get('message', "")

        self.gold += gold
        self.diamond += diamond
        self.renown += renown
        self.crystal += crystal
        self.gas += gas

        if self.gold < 0:
            raise GameException(ConfigErrorMessage.get_error_id("GOLD_NOT_ENOUGH"))
        if self.diamond < 0:
            raise GameException(ConfigErrorMessage.get_error_id("DIAMOND_NOT_ENOUGH"))
        if self.crystal < 0:
            raise GameException(ConfigErrorMessage.get_error_id("CRYSTAL_NOT_ENOUGH"))
        if self.gas < 0:
            raise GameException(ConfigErrorMessage.get_error_id("GAS_NOT_ENOUGH"))

        # update
        level_changed = False
        while True:
            need_renown = club_level_up_need_renown(self.level)
            next_level_id = ConfigClubLevel.get(self.level).next_level_id
            if not next_level_id:
                if self.renown >= need_renown:
                    self.renown = need_renown - 1
                break

            if self.renown < need_renown:
                break

            self.renown -= need_renown
            self.level += 1
            level_changed = True

        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'club.level': self.level,
                'club.renown': self.renown,
                'club.gold': self.gold,
                'club.diamond': self.diamond,
                'club.crystal': self.crystal,
                'club.gas': self.gas,
            }}
        )

        if level_changed:
            club_level_up_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
                new_level=self.level
            )

            self.send_staff_slots_notify()

        self.send_notify()

        if gold or diamond:
            FinanceStatistics(self.server_id, self.char_id).add_log(
                    gold=gold,
                    diamond=diamond,
                    message=message
            )


    def buy_slot(self):
        with Resource(self.server_id, self.char_id).check(diamond=-BUY_STAFF_SLOT_COST, message=u"Club Buy Slot"):
            MongoCharacter.db(self.server_id).update_one(
                {'_id': self.char_id},
                {'$inc': {'buy_slots': 1}}
            )

        self.send_staff_slots_notify()

    def batch_add_zhimingdu_for_match_staffs(self, zhimingdu=1):
        # 降低IO，批量操作
        updater = {}
        for s in self.match_staffs:
            updater['staffs.{0}.zhimingdu'.format(s)] = zhimingdu

        MongoStaff.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$inc': updater}
        )

        StaffManger(self.server_id, self.char_id).send_notify(staff_ids=self.match_staffs)

    def dumps(self):
        """

        :rtype : str
        """
        return base64.b64encode(dill.dumps(self))

    @classmethod
    def loads(cls, data):
        """

        :rtype : Club
        """
        return dill.loads(base64.b64decode(data))

    def send_notify(self):
        msg = self.make_protomsg()
        notify = ClubNotify()
        notify.club.MergeFrom(msg)
        MessagePipe(self.char_id).put(notify)

    def send_staff_slots_notify(self):
        notify = ClubStaffSlotsAmountNotify()
        notify.amount = self.max_slots_amount
        notify.cost_diamond = BUY_STAFF_SLOT_COST
        MessagePipe(self.char_id).put(msg=notify)
