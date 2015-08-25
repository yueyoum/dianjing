# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2015-08-03 16:21
Description:

"""

from core.task import TaskManager

from core.signals import (
    challenge_match_signal,
    friend_match_signal,
    chat_signal,
    league_match_signal,
)


def challenge_match(server_id, char_id, challenge_id, win, **kwargs):
    TaskManager(server_id, char_id).trig(1, 1)

def friend_match(server_id, char_id, friend_id, win, **kwargs):
    TaskManager(server_id, char_id).trig(2, 1)

def chat(server_id, char_id, **kwargs):
    TaskManager(server_id, char_id).trig(3, 1)

def league_match(server_id, char_id, **kwargs):
    TaskManager(server_id, char_id).trig(4, 1)


challenge_match_signal.connect(
    challenge_match,
    dispatch_uid='signals.task.challenge_match'
)

friend_match_signal.connect(
    friend_match,
    dispatch_uid='signals.task.friend_match'
)

chat_signal.connect(
    chat,
    dispatch_uid='signals.task.chat'
)
