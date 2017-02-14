# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       checker
Date Created:   2016-10-28 15:51
Description:

"""

from dianjing.exception import GameException

from config import ConfigErrorMessage


def staff_exists(server_id, char_id, staff_id):
    from core.staff import StaffManger
    StaffManger(server_id, char_id).check_staff(ids=[staff_id])


class StaffWorkingChecker(object):
    def __init__(self, server_id, char_id):
        from core.formation import Formation
        from core.plunder import Plunder
        from core.inspire import Inspire
        from core.championship import Championship

        self.server_id = server_id
        self.char_id = char_id

        self.formation = Formation(server_id, char_id)

        p = Plunder(server_id, char_id)
        self.plunder_formation_1 = p.get_way_object(1)
        self.plunder_formation_2 = p.get_way_object(2)
        self.plunder_formation_3 = p.get_way_object(3)

        c = Championship(server_id, char_id)
        self.championship_formation_1 = c.get_way_object(1)
        self.championship_formation_2 = c.get_way_object(2)
        self.championship_formation_3 = c.get_way_object(3)

        self.inspire = Inspire(server_id, char_id)

    def is_not_working(self, staff_id, raise_exception=True):
        if self.formation.is_staff_in_formation(staff_id):
            if raise_exception:
                raise GameException(ConfigErrorMessage.get_error_id("STAFF_IN_FORMATION"))

            return False

        if self.plunder_formation_1.is_staff_in_formation(staff_id):
            if raise_exception:
                raise GameException(ConfigErrorMessage.get_error_id("STAFF_IN_PLUNDER_FORMATION"))

            return False

        if self.plunder_formation_2.is_staff_in_formation(staff_id):
            if raise_exception:
                raise GameException(ConfigErrorMessage.get_error_id("STAFF_IN_PLUNDER_FORMATION"))

            return False
        if self.plunder_formation_3.is_staff_in_formation(staff_id):
            if raise_exception:
                raise GameException(ConfigErrorMessage.get_error_id("STAFF_IN_PLUNDER_FORMATION"))

            return False

        if self.championship_formation_1.is_staff_in_formation(staff_id):
            if raise_exception:
                raise GameException(ConfigErrorMessage.get_error_id("STAFF_IN_CHAMPIONSHIP_FORMATION"))

            return False

        if self.championship_formation_2.is_staff_in_formation(staff_id):
            if raise_exception:
                raise GameException(ConfigErrorMessage.get_error_id("STAFF_IN_CHAMPIONSHIP_FORMATION"))

            return False

        if self.championship_formation_3.is_staff_in_formation(staff_id):
            if raise_exception:
                raise GameException(ConfigErrorMessage.get_error_id("STAFF_IN_CHAMPIONSHIP_FORMATION"))

            return False

        if self.inspire.is_staff_in(staff_id):
            if raise_exception:
                raise GameException(ConfigErrorMessage.get_error_id("INSPIRE_STAFF_IN"))

            return False

        return True
