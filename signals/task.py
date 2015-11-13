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
    ladder_match_signal,
    recruit_staff_signal,
    club_level_up_signal,
    match_staffs_set_change_signal,
    staff_property_training_signal,
    staff_exp_training_start_signal,
    staff_exp_training_speedup_signal,
    staff_broadcast_signal,
    daily_task_finish_signal,
    set_staff_in_shop_signal,
    random_event_done_signal,
    building_level_up_start_signal,
    item_got_signal,
    training_skill_item_got_signal,
    in_car_signal,
)


# update
@receiver(recruit_staff_signal, dispatch_uid='signals.task.recruit_staff_handler')
def recruit_staff_handler(server_id, char_id, staff_id, **kwargs):
    TaskManager(server_id, char_id).update(1, 0, 1)


@receiver(match_staffs_set_change_signal, dispatch_uid='signals.task.match_staffs_change_handler')
def match_staffs_change_handler(server_id, char_id, **kwargs):
    TaskManager(server_id, char_id).update(2, 0, 1)


@receiver(challenge_match_signal, dispatch_uid='signals.task.challenge_match_handler')
def challenge_match_handler(server_id, char_id, challenge_id, win, **kwargs):
    TaskManager(server_id, char_id).update(12, 0, 1)
    if win:
        TaskManager(server_id, char_id).update(3, 0, 0)


@receiver(staff_property_training_signal, dispatch_uid='signals.task.staff_property_training_handler')
def staff_property_training_handler(server_id, char_id, staff_id, **kwargs):
    TaskManager(server_id, char_id).update(4, 0, 1)


# TODO
@receiver(building_level_up_start_signal, dispatch_uid='signals.task.building_level_up_handle')
def building_level_up_handle(server_id, char_id, building_id, **kwargs):
    TaskManager(server_id, char_id).update(5, 0, 0)


@receiver(staff_exp_training_start_signal, dispatch_uid='signals.task.staff_exp_training_start_handler')
def staff_exp_training_start_handler(server_id, char_id, staff_id, **kwargs):
    TaskManager(server_id, char_id).update(6, 0, 1)


@receiver(staff_exp_training_speedup_signal, dispatch_uid='signals.task.staff_exp_training_speedup_handler')
def staff_exp_training_speedup_handler(server_id, char_id, staff_id, **kwargs):
    TaskManager(server_id, char_id).update(7, 0, 1)


@receiver(staff_broadcast_signal, dispatch_uid='signals.task.staff_broadcast_handler')
def staff_broadcast_handler(server_id, char_id, staff_id, **kwargs):
    TaskManager(server_id, char_id).update(8, 0, 1)


@receiver(ladder_match_signal, dispatch_uid='signals.task.ladder_match_handler')
def ladder_match_handler(server_id, char_id, target_id, win, **kwargs):
    TaskManager(server_id, char_id).update(9, 0, 1)


@receiver(daily_task_finish_signal, dispatch_uid='signals.task.daily_task_finish_handler')
def daily_task_finish_handler(server_id, char_id, task_id, **kwargs):
    TaskManager(server_id, char_id).update(10, 0, 1)


@receiver(club_level_up_signal, dispatch_uid='signals.task.club_level_up_handler')
def club_level_up_handler(server_id, char_id, new_level, **kwargs):
    TaskManager(server_id, char_id).update(11, 0, 0)


@receiver(friend_match_signal, dispatch_uid='signals.task.friend_match_handler')
def friend_match_handler(server_id, char_id, target_id, win, **kwargs):
    TaskManager(server_id, char_id).update(14, 0, 1)


@receiver(item_got_signal, dispatch_uid='signals.task.item_got_handler')
def item_got_handler(server_id, char_id, items, **kwargs):
    TaskManager(server_id, char_id).update(15, 0, 0)


@receiver(set_staff_in_shop_signal, dispatch_uid='signals.task.set_staff_in_shop_handler')
def set_staff_in_shop_handler(server_id, char_id, staff_id, **kwargs):
    TaskManager(server_id, char_id).update(16, 0, 1)


@receiver(in_car_signal, dispatch_uid='signals.task.in_car_handler')
def in_car_handler(server_id, char_id, **kwargs):
    TaskManager(server_id, char_id).update(17, 0, 1)


@receiver(training_skill_item_got_signal, dispatch_uid='signals.task.training_skill_item_handler')
def training_skill_item_handler(server_id, char_id, items, **kwargs):
    TaskManager(server_id, char_id).update(18, 0, 0)


@receiver(random_event_done_signal, dispatch_uid='signals.task.random_event_done_handler')
def random_event_done_handler(server_id, char_id, event_id, **kwargs):
    TaskManager(server_id, char_id).update(13, 0, 1)
    TaskManager(server_id, char_id).update(19, event_id, 1)
