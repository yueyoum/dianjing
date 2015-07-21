# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       resource
Date Created:   2015-07-21 10:17
Description:

"""

from core.base import STAFF_ATTRS
from core.package import Package

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
