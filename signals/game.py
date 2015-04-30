# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       game
Date Created:   2015-04-30 15:23
Description:

"""

from core.signals import game_start_signal
from apps.character.core import CharacterManager
from apps.club.core import ClubManager
from apps.staff.core import StaffManager

def start(char_id, **kwargs):
    if not char_id:
        return

    CharacterManager(char_id).send_notify()
    ClubManager(char_id).send_notify()
    StaffManager(char_id).send_notify()


game_start_signal.connect(
    start,
    dispatch_uid='signals.game.start'
)
