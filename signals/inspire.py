# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       inspire
Date Created:   2016-10-31 13:37
Description:

"""


from django.dispatch import receiver
from core.signals import inspire_staff_changed_signal

from core.club import Club

@receiver(inspire_staff_changed_signal, dispatch_uid='signals.inspire.inspire_staff_changed_signal')
def inspire_staff_changed_handler(server_id, char_id, staff_id, **kwargs):
    club = Club(server_id, char_id, load_staffs=False)
    club.force_load_staffs(send_notify=True)
