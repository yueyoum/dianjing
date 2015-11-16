# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       match
Date Created:   2015-10-26 17:04
Description:

"""

from django.dispatch import receiver

from core.signals import challenge_match_signal, league_match_signal
from core.training import TrainingSponsor
from core.staff import StaffManger
from core.club import Club

@receiver(challenge_match_signal, dispatch_uid='signals.match.challenge_match_handler')
def challenge_match_handler(server_id, char_id, challenge_id, win, **kwargs):
    if not win:
        return

    TrainingSponsor(server_id, char_id).open(challenge_id)

    # zhimingdu
    club = Club(server_id, char_id)
    sm = StaffManger(server_id, char_id)
    for staff_id in club.match_staffs:
        sm.update(staff_id, zhimingdu=1)


@receiver(league_match_signal, dispatch_uid='signals.match.league_match_handler')
def league_match_handler(server_id, char_id, target_id, win, **kwargs):
    if not win:
        return

    # zhimingdu
    club = Club(server_id, char_id)
    sm = StaffManger(server_id, char_id)
    for staff_id in club.match_staffs:
        sm.update(staff_id, zhimingdu=1)

