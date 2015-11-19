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
    chat_signal,
    challenge_match_signal,
    ladder_match_signal,
    friend_match_signal,
    random_event_done_signal,
    training_sponsor_start_signal,
    training_broadcast_start_signal,
    training_property_start_signal,
    training_exp_start_signal,
    training_shop_start_signal,
    training_skill_start_signal
)


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


@receiver(training_broadcast_start_signal, dispatch_uid='signals.active_value.training_broadcast_start_handler')
def training_broadcast_start_handler(server_id, char_id, staff_id, **kwargs):
    ActiveValue(server_id, char_id).trig("FUNCTION_TRAINING_TYPE_1")


@receiver(training_exp_start_signal, dispatch_uid='signals.active_value.training_exp_start_handler')
def training_exp_start_handler(server_id, char_id, staff_id, **kwargs):
    ActiveValue(server_id, char_id).trig("FUNCTION_TRAINING_TYPE_4")


@receiver(training_sponsor_start_signal, dispatch_uid='signals.active_value.training_sponsor_start_handler')
def training_sponsor_start_handler(server_id, char_id, sponsor_id, **kwargs):
    ActiveValue(server_id, char_id).trig("FUNCTION_TRAINING_TYPE_5")


@receiver(training_shop_start_signal, dispatch_uid='signals.active_value.training_shop_start_handler')
def training_shop_start_handler(server_id, char_id, staff_id, **kwargs):
    ActiveValue(server_id, char_id).trig("FUNCTION_TRAINING_TYPE_6")


@receiver(training_property_start_signal, dispatch_uid='signals.active_value.training_property_start_handler')
def training_property_start_handler(server_id, char_id, staff_id, **kwargs):
    ActiveValue(server_id, char_id).trig("FUNCTION_TRAINING_TYPE_2")


@receiver(training_skill_start_signal, dispatch_uid='signals.active_value.training_skill_start_handler')
def training_skill_start_handler(server_id, char_id, staff_id, skill_id, **kwargs):
    ActiveValue(server_id, char_id).trig("FUNCTION_TRAINING_TYPE_3")
