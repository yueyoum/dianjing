# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       staff
Date Created:   2016-05-27 15-24
Description:

"""

from django.dispatch import receiver
from core.signals import staff_new_add_signal
from core.collection import Collection


@receiver(staff_new_add_signal, dispatch_uid='signals.staff.staff_new_add_handler')
def staff_new_add_handler(server_id, char_id, oid, unique_id, send_notify, **kwargs):
    Collection(server_id, char_id).add(oid, send_notify=send_notify)
