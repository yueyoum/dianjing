# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       club
Date Created:   2015-07-03 15:09
Description:

"""

import base64
import dill

from core.mongo import MongoCharacter
from core.abstract import AbstractClub
from core.signals import club_level_up_signal
from core.statistics import FinanceStatistics
from core.talent import TalentManager

from dianjing.exception import GameException

from utils.message import MessagePipe

from config import (
    ConfigClubLevel,
    ConfigErrorMessage
)

from protomsg.club_pb2 import ClubNotify

MAX_CLUB_LEVEL = max(ConfigClubLevel.INSTANCES.keys())


def get_club_property(server_id, char_id, key, default_value=0):
    doc = MongoCharacter.db(server_id).find_one(
        {'_id': char_id},
        {'club.{0}'.format(key): 1}
    )

    return doc['club'].get(key, default_value)


class Club(AbstractClub):
    __slots__ = []

    def __init__(self, server_id, char_id):
        super(Club, self).__init__()

        self.server_id = server_id
        self.char_id = char_id

        doc = MongoCharacter.db(self.server_id).find_one({'_id': self.char_id}, {'club': 1, 'name': 1})
        club = doc['club']

        self.id = self.char_id  # 玩家ID
        self.name = club['name']  # 俱乐部名
        self.manager_name = doc['name']  # 角色名
        self.flag = club['flag']  # 俱乐部旗帜
        self.level = club['level']  # 俱乐部等级
        self.exp = club.get('exp', 0)
        self.vip = club['vip']  # vip等级
        self.gold = club['gold']  # 游戏币
        self.diamond = club['diamond']  # 钻石
        self.renown = club.get('renown', 0)

        self.crystal = club.get('crystal', 0)
        self.gas = club.get('gas', 0)

    def load_staffs(self, ids=None):
        from core.staff import StaffManger, Staff
        from core.formation import Formation

        sm = StaffManger(self.server_id, self.char_id)
        fm = Formation(self.server_id, self.char_id)

        staffs = sm.get_staffs_data(ids=ids)
        in_formation_staffs = fm.in_formation_staffs()

        staff_objs = {}
        """:type: dict[str, core.staff.Staff]"""
        for k, v in staffs.items():
            staff_objs[k] = Staff(self.server_id, self.char_id, k, v)

        for k, v in staff_objs.iteritems():
            if k in in_formation_staffs:
                self.formation_staffs.append(v)

                # 这里不用设置兵种， 进入战斗前，再设置，并计算兵种属性
                # v.formation_position = in_formation_staffs[k]['position']
                # unit_id = in_formation_staffs[k]['unit_id']
                # if unit_id:
                #     v.set_unit(um.get_unit_object(unit_id))

        talent_effect = TalentManager(self.server_id, self.char_id).get_talent_effect()
        for k in in_formation_staffs:
            staff_objs[k].talent_effect(self)
            staff_objs[k].talent_tree_effect(talent_effect)

        for _, v in staff_objs.iteritems():
            v.calculate()
            v.make_cache()

    def before_match(self):
        from core.formation import Formation
        from core.unit import UnitManager

        fm = Formation(self.server_id, self.char_id)
        in_formation_staffs = fm.in_formation_staffs()

        um = UnitManager(self.server_id, self.char_id)

        for s in self.formation_staffs:
            s.formation_position = in_formation_staffs[s.id]['position']
            unit_id = in_formation_staffs[s.id]['unit_id']
            if unit_id:
                s.set_unit(um.get_unit_object(unit_id))

    def check_money(self, diamond=0, gold=0, crystal=0, gas=0):
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

    def update(self, **kwargs):
        exp = kwargs.get('exp', 0)
        gold = kwargs.get('gold', 0)
        diamond = kwargs.get('diamond', 0)
        crystal = kwargs.get('crystal', 0)
        gas = kwargs.get('gas', 0)
        renown = kwargs.get('renown', 0)
        message = kwargs.get('message', "")

        self.gold += gold
        self.diamond += diamond
        self.exp += exp
        self.crystal += crystal
        self.gas += gas
        self.renown += renown

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
            if self.level >= MAX_CLUB_LEVEL:
                self.exp = 0
                break

            need_exp = ConfigClubLevel.get(self.level).exp
            if self.exp < need_exp:
                break

            self.exp -= need_exp
            self.level += 1
            level_changed = True

        MongoCharacter.db(self.server_id).update_one(
            {'_id': self.char_id},
            {'$set': {
                'club.level': self.level,
                'club.exp': self.exp,
                'club.gold': self.gold,
                'club.diamond': self.diamond,
                'club.crystal': self.crystal,
                'club.gas': self.gas,
                'club.renown': self.renown
            }}
        )

        if level_changed:
            club_level_up_signal.send(
                sender=None,
                server_id=self.server_id,
                char_id=self.char_id,
                new_level=self.level
            )

        self.send_notify()

        if gold or diamond:
            FinanceStatistics(self.server_id, self.char_id).add_log(
                gold=gold,
                diamond=diamond,
                message=message
            )

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
