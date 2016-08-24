# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       club
Date Created:   2015-07-23 18:31
Description:

"""
from django.dispatch import receiver
from core.signals import club_level_up_signal
from core.task import TaskDaily
from core.energy import Energy
from core.unit import UnitManager
from core.formation import Formation
from core.welfare import Welfare
from core.plunder import Plunder

from config import ConfigClubLevel

@receiver(club_level_up_signal, dispatch_uid='signals.club.club_level_up_handler')
def club_level_up_handler(server_id, char_id, new_level, **kwargs):
    TaskDaily(server_id, char_id).try_open()

    energy_add = ConfigClubLevel.get(new_level-1).energy
    Energy(server_id, char_id).add(energy_add)

    UnitManager(server_id, char_id).try_unlock()
    Formation(server_id, char_id).try_open_slots(new_level)
    Welfare(server_id, char_id).send_level_reward_notify()
    Plunder(server_id, char_id).try_initialize()
