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

from dianjing.exception import GameException

from utils.message import MessagePipe

from config import (
    ConfigClubLevel,
    ConfigErrorMessage
)

from protomsg.club_pb2 import ClubNotify


def club_level_up_need_renown(level):
    return ConfigClubLevel.get(level).renown


class Club(AbstractClub):
    __slots__ = [
        'server_id', 'char_id',
    ]

    def __init__(self, server_id, char_id):
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

    def load_formation_staffs(self):
        from core.formation import Formation
        self.formation_staffs = Formation(self.server_id, self.char_id).get_formation_staffs()


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
