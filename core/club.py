# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       club
Date Created:   2015-07-03 15:09
Description:

"""

from core.mongo import MongoCharacter, MongoStaff
from core.abstract import AbstractClub
from core.signals import match_staffs_set_done_signal, club_level_up_signal, match_staffs_set_change_signal
from core.staff import StaffManger
from core.resource import Resource

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
        self.policy = club.get('policy', 1)  # 战术

        self.match_staffs = club.get('match_staffs', [])  # 出战员工
        self.tibu_staffs = club.get('tibu_staffs', [])  # 替补员工

        self.buy_slots = doc.get('buy_slots', 0)

        if load_staff:
            self.load_match_staffs()

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
        return staff_id in self.match_staffs or staff_id in self.tibu_staffs

    def set_policy(self, policy):
        if not ConfigPolicy.get(policy):
            raise GameException(ConfigErrorMessage.get_error_id('POLICY_NOT_EXIST'))

        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {'club.policy': policy}}
        )

        self.policy = policy
        self.send_notify()

    def set_match_staffs(self, staff_ids, trig_signal=True):
        if len(staff_ids) != 10:
            raise GameException(ConfigErrorMessage.get_error_id("BAD_MESSAGE"))

        if not StaffManger(self.server_id, self.char_id).has_staff([i for i in staff_ids if i != 0]):
            raise GameException(ConfigErrorMessage.get_error_id('STAFF_NOT_EXIST'))

        match_staffs = staff_ids[:5]
        tibu_staffs = staff_ids[5:]

        doc = MongoCharacter.db(self.server_id).find_one(
            {'_id': self.char_id},
            {
                'club.match_staffs': 1,
                'club.tibu_staffs': 1
            }
        )

        old_staff_ids = doc['club']['match_staffs'] + doc['club']['tibu_staffs']
        if trig_signal and staff_ids != old_staff_ids:
            match_staffs_set_change_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
            )

        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'club.match_staffs': match_staffs,
                'club.tibu_staffs': tibu_staffs
            }}
        )

        self.match_staffs = match_staffs
        self.tibu_staffs = tibu_staffs
        self.load_match_staffs()

        if trig_signal and all([i != 0 for i in match_staffs]):
            # set done
            match_staffs_set_done_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
                match_staffs=match_staffs
            )

        self.send_notify()

    def update(self, **kwargs):
        renown = kwargs.get('renown', 0)
        gold = kwargs.get('gold', 0)
        diamond = kwargs.get('diamond', 0)

        self.gold += gold
        self.diamond += diamond
        self.renown += renown

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
