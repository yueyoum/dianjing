# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       arena
Date Created:   2016-07-06 11-08
Description:

"""

from django.dispatch import receiver
from core.signals import arena_match_signal

from core.system import BroadCast

@receiver(arena_match_signal, dispatch_uid='signals.arena.match_handler')
def match_handler(server_id, char_id, target_id, my_rank, rival_rank, win, **kwargs):
    if win:
        b = BroadCast(server_id, char_id)
        b.cast_arena_match_notify(target_id, rival_rank)