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

from config import ConfigErrorMessage


class Resource(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

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
