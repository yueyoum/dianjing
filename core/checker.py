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

def staff_not_in_formation(server_id, char_id, staff_id):
    from core.formation import Formation
    from core.plunder import Plunder
    from core.inspire import Inspire

    if Formation(server_id, char_id).is_staff_in_formation(staff_id):
        raise GameException(ConfigErrorMessage.get_error_id("STAFF_IN_FORMATION"))

    if Plunder(server_id, char_id).find_way_id_by_staff_id(staff_id):
        raise GameException(ConfigErrorMessage.get_error_id("STAFF_IN_PLUNDER_FORMATION"))

    Inspire(server_id, char_id).check_staff_in(staff_id)
