# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       resource
Date Created:   2015-07-21 10:17
Description:

"""

from contextlib import contextmanager

from core.base import STAFF_ATTRS
from core.package import Package
from dianjing.exception import GameException
from config import ConfigErrorMessage


class Resource(object):
    def __init__(self, server_id, char_id):
        self.server_id = server_id
        self.char_id = char_id

    def add(self, **kwargs):
        staff_id = kwargs.pop('staff_id', None)

        p = Package.new(**kwargs)
        self.add_package(p, staff_id=staff_id)


    def add_from_package_id(self, package_id, staff_id=None):

        p = Package.generate(package_id)
        self.add_package(p, staff_id=staff_id)


    def add_package(self, package, staff_id=None):
        """

        :type package: core.package.Package
        """
        from core.club import Club
        from core.staff import StaffManger

        if package.club_renown or package.gold or package.diamond:
            club_data = {
                'renown': package.club_renown,
                'gold': package.gold,
                'diamond': package.diamond,
            }

            club = Club(self.server_id, self.char_id)
            club.update(**club_data)

        if staff_id:
            staff_data = {
                'exp': package.staff_exp,
            }

            for attr in STAFF_ATTRS:
                staff_data[attr] = getattr(package, attr)

            sm = StaffManger(self.server_id, self.char_id)
            sm.update(staff_id, **staff_data)


    @contextmanager
    def check(self, **kwargs):
        data = self.data_analysis(**kwargs)
        check_list = self._pre_check_list(data)

        yield

        self._post_check(check_list)


    def data_analysis(self, **kwargs):
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


    def _post_check(self, check_list):
        for func in check_list:
            try:
                func.next()
            except StopIteration:
                pass


    def _club_resource_check(self, gold=0, diamond=0):
        from core.club import Club

        club = Club(self.server_id, self.char_id)

        if abs(gold) > club.gold and gold < 0:
            raise GameException(ConfigErrorMessage.get_error_id('NOT_ENOUGH_GOLD'))
        elif abs(diamond) > club.diamond and diamond < 0:
            raise GameException(ConfigErrorMessage.get_error_id('NOT_ENOUGH_DIAMOND'))

        yield

        club.update(gold=gold, diamond=diamond)
