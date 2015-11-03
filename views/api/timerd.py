# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       timerd
Date Created:   2015-11-02 13:29
Description:

"""
import json
from django.http import JsonResponse

from core.building import BuildingManager
from core.training import TrainingExp, TrainingProperty, TrainingBroadcast


def building_levelup_callback(request):
    data = request.POST['data']
    data = json.loads(data)

    server_id = data['sid']
    char_id = data['cid']
    building_id = data['building_id']

    bm = BuildingManager(server_id, char_id)
    timestamp = bm.levelup_callback(building_id)

    return JsonResponse({'end': timestamp})


def training_exp_callback(request):
    data = request.POST['data']
    data = json.loads(data)

    server_id = data['sid']
    char_id = data['cid']
    slot_id = data['slot_id']

    te = TrainingExp(server_id, char_id)
    timestamp = te.callback(slot_id)
    return JsonResponse({'end': timestamp})


def training_property_callback(request):
    data = request.POST['data']
    data = json.loads(data)

    server_id = data['sid']
    char_id = data['cid']
    staff_id = data['staff_id']

    tp = TrainingProperty(server_id, char_id)
    timestamp = tp.callback(staff_id)
    return JsonResponse({'end': timestamp})


def training_broadcast_callback(request):
    data = request.POST['data']
    data = json.loads(data)

    server_id = data['sid']
    char_id = data['cid']
    slot_id = data['slot_id']

    tb = TrainingBroadcast(server_id, char_id)
    timestamp = tb.callback(slot_id)
    return JsonResponse({'end': timestamp})
