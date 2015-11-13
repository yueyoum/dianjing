# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       building
Date Created:   2015-11-03 16:06
Description:

"""

from django.dispatch import receiver

from core.signals import building_level_up_done_signal
from core.building import BuildingBusinessCenter, BuildingTrainingCenter

from core.training import TrainingBroadcast, TrainingExp

@receiver(building_level_up_done_signal, dispatch_uid='signals.building.level_up_handler')
def level_up_handler(server_id, char_id, building_id, **kwargs):
    if building_id == BuildingBusinessCenter.BUILDING_ID:
        tb = TrainingBroadcast(server_id, char_id)
        tb.open_slots_by_building_level_up()

    elif building_id == BuildingTrainingCenter.BUILDING_ID:
        te = TrainingExp(server_id, char_id)
        te.open_slots_by_building_level_up()
