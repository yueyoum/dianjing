# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       vip
Date Created:   2016-05-27 12-32
Description:

"""

from django.dispatch import receiver
from core.signals import vip_level_up_signal
from core.task import TaskDaily


@receiver(vip_level_up_signal, dispatch_uid='signals.vip.vip_level_up_signal')
def vip_level_up_signal(server_id, char_id, new_level, **kwargs):
    TaskDaily(server_id, char_id).try_open()