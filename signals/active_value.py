# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       active_value
Date Created:   2015-10-10 10:20
Description:

"""

from django.dispatch import receiver

from core.active_value import ActiveValue
from core.signals import (
    training_got_reward_signal,
    chat_signal,
    challenge_match_signal,
    ladder_match_signal,
    friend_match_signal,
    random_event_done_signal,
)

from config import ConfigTraining


@receiver(training_got_reward_signal, dispatch_uid='signals.active_value.training_got_reward_handler')
def training_got_reward_handler(server_id, char_id, training_id, **kwargs):
    config = ConfigTraining.get(training_id)
    function_name = "FUNCTION_TRAINING_TYPE_{0}".format(config.tp)

    ActiveValue(server_id, char_id).trig(function_name)


@receiver(chat_signal, dispatch_uid='signals.active_value.chat_handler')
def chat_handler(server_id, char_id, **kwargs):
    ActiveValue(server_id, char_id).trig("FUNCTION_CHAT")


@receiver(challenge_match_signal, dispatch_uid='signals.active_value.challenge_match_handler')
def challenge_match_handler(server_id, char_id, challenge_id, win, **kwargs):
    ActiveValue(server_id, char_id).trig("FUNCTION_CHALLENGE_MATCH")


@receiver(ladder_match_signal, dispatch_uid='signals.active_value.ladder_match_handler')
def ladder_match_handler(server_id, char_id, target_id, win, **kwargs):
    ActiveValue(server_id, char_id).trig("FUNCTION_LADDER_MATCH")


@receiver(friend_match_signal, dispatch_uid='signals.active_value.friend_match_handler')
def friend_match_handler(server_id, char_id, target_id, win, **kwargs):
    ActiveValue(server_id, char_id).trig("FUNCTION_FRIEND_MATCH")


@receiver(random_event_done_signal, dispatch_uid='signals.active_value.random_event_done_handler')
def random_event_done_handler(server_id, char_id, event_id, **kwargs):
    ActiveValue(server_id, char_id).trig("FUNCTION_RANDOM_EVENT")
