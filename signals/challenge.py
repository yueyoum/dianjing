# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2016-10-31 10:06
Description:

"""

from django.dispatch import receiver
from core.signals import challenge_match_signal

from core.task import TaskMain
from core.inspire import Inspire

@receiver(challenge_match_signal, dispatch_uid='signals.challenge.challenge_match_signal')
def challenge_match_handler(server_id, char_id, challenge_id, star, **kwargs):
    TaskMain(server_id, char_id).trig(challenge_id)
    if star > 0:
        Inspire(server_id, char_id).try_open_slots()
