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


def staff_not_working(server_id, char_id, staff_id, raise_exception=True):
    from core.formation import Formation
    from core.plunder import Plunder
    from core.inspire import Inspire

    if Formation(server_id, char_id).is_staff_in_formation(staff_id):
        if raise_exception:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_IN_FORMATION"))

        return False

    if Plunder(server_id, char_id).find_way_id_by_staff_id(staff_id):
        if raise_exception:
            raise GameException(ConfigErrorMessage.get_error_id("STAFF_IN_PLUNDER_FORMATION"))

        return False

    # TODO championship formation check

    if Inspire(server_id, char_id).is_staff_in(staff_id):
        if raise_exception:
            raise GameException(ConfigErrorMessage.get_error_id("INSPIRE_STAFF_IN"))

        return False

    return True
