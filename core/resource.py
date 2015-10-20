# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       resource
Date Created:   2015-07-21 10:17
Description:

"""

from contextlib import contextmanager
from dianjing.exception import GameException

from core.base import STAFF_ATTRS
from core.package import PackageBase
from core.statistics import FinanceStatistics

from config import ConfigErrorMessage


class Resource(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id


    def save_drop(self, drop, message=""):
        """

        :type drop: PackageBase
        """
        from core.club import Club
        from core.ladder import Ladder

        if drop.club_renown or drop.gold or drop.diamond:
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

        if drop.ladder_score:
            Ladder(self.server_id, self.char_id).add_score(drop.ladder_score)

        # TODO drop.league_score ?

        # if drop.trainings:
        #     tb = TrainingBag(self.server_id, self.char_id)
        #     for tid, amount in drop.trainings:
        #         for i in range(amount):
        #             tb.add_from_raw_training(tid)

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
