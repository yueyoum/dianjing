# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       signals
Date Created:   2015-04-30 15:20
Description:

"""

from django.dispatch import Signal

char_created_signal = Signal(providing_args=['char_id', 'char_name'])
game_start_signal = Signal(providing_args=['server_id', 'char_id'])
match_staffs_set_done_signal = Signal(providing_args=['server_id', 'char_id', 'match_staffs'])

challenge_match_signal = Signal(providing_args=['server_id', 'char_id', 'challenge_id', 'win'])
friend_match_signal = Signal(providing_args=['server_id', 'char_id', 'friend_id', 'win'])
league_match_signal = Signal(providing_args=['server_id', 'char_id'])
chat_signal = Signal(providing_args=['server_id', 'char_id'])
