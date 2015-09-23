# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       purchase
Date Created:   2015-09-17 17:33
Description:

"""

from django.dispatch import receiver
from core.signals import purchase_done_signal
from core.sponsor import SponsorManager

@receiver(purchase_done_signal, dispatch_uid='signals.purchase.purchase_done_handler')
def purchase_done_handler(server_id, char_id, diamond, **kwargs):
    SponsorManager(server_id, char_id).purchase(diamond)
