# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       staff
Date Created:   2016-05-27 15-24
Description:

"""

from django.dispatch import receiver
from core.signals import staff_new_add_signal, recruit_staff_diamond_signal
from core.collection import Collection
from core.system import BroadCast


@receiver(staff_new_add_signal, dispatch_uid='signals.staff.staff_new_add_handler')
def staff_new_add_handler(server_id, char_id, oid, unique_id, force_load_staffs, **kwargs):
    Collection(server_id, char_id).add(oid, force_load_staffs=force_load_staffs)


@receiver(recruit_staff_diamond_signal, dispatch_uid='signals.staff.recruit_diamond')
def recruit_staff_diamond_handler(server_id, char_id, times, staffs, **kwargs):
    b = BroadCast(server_id, char_id)
    for _sid, _amount in staffs:
        b.cast_diamond_recruit_staff_notify(_sid)
