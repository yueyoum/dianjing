# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       task_condition
Date Created:   2016-08-05 18:22
Description:

"""

from django.dispatch import receiver
from core.signals import task_condition_trig_signal

from core.task import TaskDaily
from core.activity import ActivityNewPlayer

from config import ConfigTaskCondition


@receiver(task_condition_trig_signal, dispatch_uid='signals.task_condition.trig_handler')
def trig_handler(server_id, char_id, condition_name, **kwargs):
    condition_ids = ConfigTaskCondition.get_condition_ids_by_name(condition_name)
    if condition_ids:
        t = TaskDaily(server_id, char_id)
        a = ActivityNewPlayer(server_id, char_id)

        for i in condition_ids:
            t.trig(i)
            a.trig(i)
