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

