# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       resource
Date Created:   2015-07-21 10:17
Description:

"""

from contextlib import contextmanager
from dianjing.exception import GameException

from core.statistics import FinanceStatistics

from config import ConfigErrorMessage, ConfigItemNew

from protomsg.package_pb2 import Drop as MsgDrop

MONEY = {
    30000: 'diamond', # 钻石
    30001: 'gold',    # 金币
    30002: 'renown',  # 声望
    30003: 'crystal', # 水晶
    30004: 'gas',     # 气矿
}

_MONEY_REVERSE = {v: k for k, v in MONEY.iteritems()}

TALENT_ITEM_ID = 30006


def item_id_to_money_text(_id):
    return MONEY[_id]

def money_text_to_item_id(text):
    return _MONEY_REVERSE[text]


def filter_money(items):
    # items: [(id, amount), (id, amount)...]
    """

    :rtype: dict[string, int]
    """
    money = {}
    for _id, _amount in items:
        name = MONEY.get(_id, None)
        if not name:
            continue

        if name in money:
            money[name] += _amount
        else:
            money[name] = _amount

    return money


def filter_bag_item(items):
    """

    :rtype: list
    """
    return [(_id, _amount) for _id, _amount in items if _id not in MONEY]


class ResourceClassification(object):
    __slots__ = ['money', 'bag', 'staff', 'talent_point']

    def __init__(self):
        self.money = []
        self.bag = []
        self.staff = []
        self.talent_point = 0

    @classmethod
    def classify(cls, items):
        # type: (list) -> ResourceClassification
        # items: [(id, amount)...]
        money = {}
        bag = {}
        staff = {}
        talent_point = 0

        for _id, _amount in items:
            if _id == TALENT_ITEM_ID:
                talent_point += _amount
                continue

            tp = ConfigItemNew.get(_id).tp
            if tp == 3:
                if _id in money:
                    money[_id] += _amount
                else:
                    money[_id] = _amount
            elif tp == 6:
                if _id in staff:
                    staff[_id] += _amount
                else:
                    staff[_id] = _amount
            else:
                if _id in bag:
                    bag[_id] += _amount
                else:
                    bag[_id] = _amount

        obj = cls()
        obj.money = money.items()
        obj.bag = bag.items()
        obj.staff = staff.items()
        obj.talent_point = talent_point

        return obj

    def money_as_text_dict(self):
        # type: () -> dict[str, int]
        res = {}
        for _id, _amount in self.money:
            res[MONEY[_id]] = _amount

        return res

    def check_exist(self, server_id, char_id):
        from core.club import Club
        from core.bag import Bag
        from core.staff import StaffManger
        from core.talent import TalentManager

        money_text = self.money_as_text_dict()
        Club(server_id, char_id).check_money(**money_text)
        Bag(server_id, char_id).check_items(self.bag)
        StaffManger(server_id, char_id).check_original_staff_is_initial_state(self.staff)
        TalentManager(server_id, char_id).check_talent_points(self.talent_point)

    def remove(self, server_id, char_id):
        from core.club import Club
        from core.bag import Bag
        from core.staff import StaffManger
        from core.talent import TalentManager

        money_text = self.money_as_text_dict()
        money_text = {k: -v for k, v in money_text.iteritems()}
        Club(server_id, char_id).update(**money_text)

        bag = Bag(server_id, char_id)
        for _id, _amount in self.bag:
            bag.remove_by_item_id(_id, _amount)

        sm = StaffManger(server_id, char_id)
        for _id, _amount in self.staff:
            for _ in range(_amount):
                sm.remove_initial_state_staff(_id)

        TalentManager(server_id, char_id).deduct_talent_points(self.talent_point)

    def add(self, server_id, char_id):
        from core.club import Club
        from core.bag import Bag
        from core.staff import StaffManger
        from core.talent import TalentManager

        money_text = self.money_as_text_dict()
        Club(server_id, char_id).update(**money_text)

        bag = Bag(server_id, char_id)
        for _id, _amount in self.bag:
            bag.add(_id, amount=_amount)

        sm = StaffManger(server_id, char_id)
        for _id, _amount in self.staff:
            for _ in range(_amount):
                sm.add(_id)

        TalentManager(server_id, char_id).add_talent_points(self.talent_point)

    def make_protomsg(self):
        msg = MsgDrop()
        for _id, _amount in self.money:
            msg_item = msg.items.add()
            msg_item.id = _id
            msg_item.amount = _amount

        for _id, _amount in self.bag:
            msg_item = msg.items.add()
            msg_item.id = _id
            msg_item.amount = _amount

        for _id, _amount in self.staff:
            msg_item = msg.items.add()
            msg_item.id = _id
            msg_item.amount = _amount

        if self.talent_point:
            msg_item = msg.items.add()
            msg_item.id = TALENT_ITEM_ID
            msg_item.amount = self.talent_point

        return msg


class Resource(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    # NEW API
    def add(self, items, message=""):
        # items: [(id, amount), (id, amount)...]
        from core.club import Club
        from core.bag import Bag

        money = filter_money(items)
        bag = filter_bag_item(items)

        if money:
            Club(self.server_id, self.char_id).update(**money)

            gold = money.get('gold', 0)
            diamond = money.get('diamond', 0)

            if gold or diamond:
                FinanceStatistics(self.server_id, self.char_id).add_log(
                        gold=gold, diamond=diamond, message=message
                )

        if bag:
            b = Bag(self.server_id, self.char_id)
            for _id, _amount in bag:
                b.add(_id, amount=_amount)


    def save_drop(self, drop, message=""):
        """
        :type drop: core.package.Drop
        """

        if drop.club_renown or drop.gold or drop.diamond:
            self.__save_club_drop(drop, message)

        if drop.training_match_score:
            self.__save_training_match_drop(drop.training_match_score)

        if drop.items:
            self.__save_item_drop(drop.items)

        if drop.staff_cards:
            self.__save_staff_cards(drop.staff_cards)

        if drop.ladder_score:
            self.__save_ladder_drop(drop.ladder_score)

    def __save_club_drop(self, drop, message):
        from core.club import Club

        club_data = {
            'renown': drop.club_renown,
            'gold': drop.gold,
            'diamond': drop.diamond,
        }

        club = Club(self.server_id, self.char_id)
        club.update(**club_data)

        if drop.gold or drop.diamond:
            FinanceStatistics(self.server_id, self.char_id).add_log(
                    gold=drop.gold, diamond=drop.diamond, message=message
            )

    def __save_training_match_drop(self, score):
        from core.training_match import TrainingMatch
        TrainingMatch(self.server_id, self.char_id).add_score(score)

    def __save_item_drop(self, items):
        from core.item import ItemManager
        im = ItemManager(self.server_id, self.char_id)
        for _id, _amount in items:
            im.add_item(_id, amount=_amount)

    def __save_staff_cards(self, staff_cards):
        from core.item import ItemManager
        im = ItemManager(self.server_id, self.char_id)
        for _id, _amount in staff_cards:
            im.add_staff_card(_id, 0, _amount)

    def __save_ladder_drop(self, score):
        from core.ladder.ladder import Ladder
        Ladder(self.server_id, self.char_id).add_score(score, send_notify=True)

    @contextmanager
    def check(self, **kwargs):
        message = kwargs.pop("message", "")
        data = self.data_analysis(**kwargs)
        check_list = self._pre_check_list(data)

        yield

        self._post_check(check_list)

        if data['gold'] or data['diamond']:
            FinanceStatistics(self.server_id, self.char_id).add_log(
                    gold=data['gold'],
                    diamond=data['diamond'],
                    message=message
            )

    @staticmethod
    def data_analysis(**kwargs):
        data = {
            'gold': kwargs.get('gold', 0),
            'diamond': kwargs.get('diamond', 0),
        }
        return data

    def _pre_check_list(self, data):
        check_list = []
        if data['gold'] or data['diamond']:
            check_list.append(self._club_resource_check(data['gold'], data['diamond']))

        for cb in check_list:
            cb.next()

        return check_list

    @staticmethod
    def _post_check(check_list):
        for func in check_list:
            try:
                func.next()
            except StopIteration:
                pass

    def _club_resource_check(self, gold=0, diamond=0):
        from core.club import Club

        club = Club(self.server_id, self.char_id)

        if abs(gold) > club.gold and gold < 0:
            raise GameException(ConfigErrorMessage.get_error_id('GOLD_NOT_ENOUGH'))
        elif abs(diamond) > club.diamond and diamond < 0:
            raise GameException(ConfigErrorMessage.get_error_id('DIAMOND_NOT_ENOUGH'))

        yield

        club.update(gold=gold, diamond=diamond)
