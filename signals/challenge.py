# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2015-08-03 16:21
Description:

"""

from core.signals import challenge_match_signal
from core.task import TaskManager


def match(server_id, char_id, challenge_id, win, **kwargs):
    TaskManager(server_id, char_id).update(task_id=1, num=1)

challenge_match_signal.connect(
    match,
    dispatch_uid='signals.challenge.match'
)
