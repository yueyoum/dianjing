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

@receiver(arena_match_signal, dispatch_uid='signals.arena.arena_match_handler')
def arena_match_handler(server_id, char_id, target_id, target_name, my_rank, target_rank, win, continue_win, **kwargs):
    if continue_win in [3, 5, 10]:
        b = BroadCast(server_id, char_id)
        b.cast_arena_match_notify(continue_win)