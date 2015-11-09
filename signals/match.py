# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       match
Date Created:   2015-10-26 17:04
Description:

"""

from django.dispatch import receiver

from core.signals import challenge_match_signal, staff_any_match_signal
from core.training import TrainingSponsor
from core.staff import StaffManger

@receiver(challenge_match_signal, dispatch_uid='signals.match.challenge_match_handler')
def challenge_match_handler(server_id, char_id, challenge_id, win, **kwargs):
    if not win:
        return

    TrainingSponsor(server_id, char_id).open(challenge_id)


@receiver(staff_any_match_signal, dispatch_uid='signals.match.staff_any_match_handler')
def staff_any_match_handler(server_id, char_id, staff_id, win, **kwargs):
    if not win:
        return

    StaffManger(server_id, char_id).update(staff_id, zhimingdu=1)
