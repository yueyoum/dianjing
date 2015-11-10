# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       challenge
Date Created:   2015-08-03 16:21
Description:

"""
from django.dispatch import receiver

from core.task import TaskManager
from core.signals import (
    challenge_match_signal,
    friend_match_signal,
    league_match_signal,
    ladder_match_signal,
    join_cup_signal,
    chat_signal,
    friend_ok_signal,
    recruit_staff_signal,
    club_level_up_signal,
    staff_level_up_signal,
    match_staffs_set_change_signal,
    staff_property_training_signal,
    building_training_center_level_up_signal,
    staff_exp_training_signal,
    staff_exp_training_speedup_signal,
    staff_broadcast_signal,
    building_league_center_level_up_signal,
)


@receiver(league_match_signal, dispatch_uid='signals.task.league_match_handler')
def league_match_handler(server_id, char_id, target_id, win, **kwargs):
    TaskManager(server_id, char_id).update(4, 1)


@receiver(join_cup_signal, dispatch_uid='signals.task.join_cup_handler')
def join_cup_handler(server_id, char_id, **kwargs):
    TaskManager(server_id, char_id).update(7, 1)


@receiver(chat_signal, dispatch_uid='signals.task.chat_handler')
def chat_handler(server_id, char_id, **kwargs):
    TaskManager(server_id, char_id).update(3, 1)


@receiver(friend_ok_signal, dispatch_uid='signals.task.friend_ok_handler')
def friend_ok_handler(server_id, char_id, friend_id, **kwargs):
    TaskManager(server_id, char_id).update(1, 1)


@receiver(staff_level_up_signal, dispatch_uid='signals.task.staff_level_up_handler')
def staff_level_up_handler(server_id, char_id, staff_id, new_level, **kwargs):
    TaskManager(server_id, char_id).update(10, 1)




@receiver(recruit_staff_signal, dispatch_uid='signals.task.recruit_staff_handler')
def recruit_staff_handler(server_id, char_id, staff_id, **kwargs):
    TaskManager(server_id, char_id).update(1, 1)


@receiver(match_staffs_set_change_signal, dispatch_uid='signals.task.match_staffs_change_handler')
def match_staffs_change_handler(server_id, char_id, **kwargs):
    TaskManager(server_id, char_id).update(2, 1)


@receiver(challenge_match_signal, dispatch_uid='signals.task.challenge_match_handler')
def challenge_match_handler(server_id, char_id, challenge_id, win, **kwargs):
    TaskManager(server_id, char_id).update(3, challenge_id)


@receiver(staff_property_training_signal, dispatch_uid='signals.task.staff_property_training_handler')
def staff_property_training_handler(server_id, char_id, staff_id, **kwargs):
    TaskManager(server_id, char_id).update(4, 1)


@receiver(building_training_center_level_up_signal, dispatch_uid='signals.task.training_center_level_up_handler')
def training_center_level_up_handler(server_id, char_id, new_level, **kwargs):
    TaskManager(server_id, char_id).update(6, new_level)


@receiver(staff_exp_training_signal, dispatch_uid='signals.task.staff_exp_training_handler')
def staff_exp_training_handler(server_id, char_id, staff_id, **kwargs):
    TaskManager(server_id, char_id).update(7, 1)


@receiver(staff_exp_training_speedup_signal, dispatch_uid='signals.task.staff_exp_training_speedup_handler')
def staff_exp_training_speedup_handler(server_id, char_id, **kwargs):
    TaskManager(server_id, char_id).update(8, 1)


@receiver(staff_broadcast_signal, dispatch_uid='signals.task.staff_broadcast_handler')
def staff_broadcast_handler(server_id, char_id, staff_id, **kwargs):
    TaskManager(server_id, char_id).update(9, 1)


@receiver(building_league_center_level_up_signal, dispatch_uid='signals.task.building_league_center_level_up_handler')
def building_league_center_level_up_handler(server_id, char_id, new_level, **kwargs):
    TaskManager(server_id, char_id).update(10, new_level)


@receiver(ladder_match_signal, dispatch_uid='signals.task.ladder_match_handler')
def ladder_match_handler(server_id, char_id, target_id, win, **kwargs):
    TaskManager(server_id, char_id).update(11, 1)


@receiver(club_level_up_signal, dispatch_uid='signals.task.club_level_up_handler')
def club_level_up_handler(server_id, char_id, new_level, **kwargs):
    TaskManager(server_id, char_id).update(13, new_level)


@receiver(friend_match_signal, dispatch_uid='signals.task.friend_match_handler')
def friend_match_handler(server_id, char_id, target_id, win, **kwargs):
    TaskManager(server_id, char_id).update(16, 1)

