# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       signals
Date Created:   2015-04-30 15:20
Description:

"""

from django.dispatch import Signal

game_start_signal = Signal(providing_args=['char_id'])
