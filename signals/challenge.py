# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2016-10-31 10:06
Description:

"""

from django.dispatch import receiver
from core.signals import challenge_match_signal

from core.formation import Formation
from core.task import TaskMain, TaskDaily
from core.inspire import Inspire
from core.plunder import Plunder
from core.activity import ActivityChallenge


@receiver(challenge_match_signal, dispatch_uid='signals.challenge.challenge_match_signal')
def challenge_match_handler(server_id, char_id, challenge_id, star, **kwargs):
    TaskMain(server_id, char_id).trig(challenge_id)
    if star > 0:
        Formation(server_id, char_id).try_open_slots()
        Inspire(server_id, char_id).try_open_slots()
        TaskDaily(server_id, char_id).try_open()
        Plunder(server_id, char_id).try_initialize()
        ActivityChallenge(server_id, char_id).trig_notify(challenge_id)
