# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       match
Date Created:   2015-10-26 17:04
Description:

"""

from django.dispatch import receiver

from core.signals import challenge_match_signal, league_match_signal
from core.club import Club

