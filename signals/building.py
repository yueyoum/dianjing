# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       building
Date Created:   2015-11-03 16:06
Description:

"""

from django.dispatch import receiver

from core.signals import (
    building_business_center_level_up_signal,
    building_sponsor_center_level_up_signal,
    building_league_center_level_up_signal,
    building_staff_center_level_up_signal,
    building_task_center_level_up_signal,
    building_training_center_level_up_signal
)

from core.training import TrainingBroadcast, TrainingExp

@receiver(building_business_center_level_up_signal, dispatch_uid='signals.building.business_level_up_handler')
def business_level_up_handler(server_id, char_id, new_level, **kwargs):
    tb = TrainingBroadcast(server_id, char_id)
    tb.open_slots_by_building_level_up()


@receiver(building_training_center_level_up_signal, dispatch_uid='signals.building.training_level_up_handler')
def training_level_up_handler(server_id, char_id, new_level, **kwargs):
    te = TrainingExp(server_id, char_id)
    te.open_slots_by_building_level_up()
