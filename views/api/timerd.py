# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       timerd
Date Created:   2015-11-02 13:29
Description:

"""
import json
from django.http import HttpResponse

from core.building import BuildingManager

from core.auction import AuctionManager
from core.challenge import Challenge


def building_levelup_callback(request):
    data = request.POST['data']
    data = json.loads(data)

    server_id = data['sid']
    char_id = data['cid']
    building_id = data['building_id']

    bm = BuildingManager(server_id, char_id)
    bm.levelup_callback(building_id)

    return HttpResponse()


def training_exp_callback(request):
    data = request.POST['data']
    data = json.loads(data)

    server_id = data['sid']
    char_id = data['cid']
    slot_id = data['slot_id']

    te = TrainingExp(server_id, char_id)
    te.callback(slot_id)
    return HttpResponse()


def training_property_callback(request):
    data = request.POST['data']
    data = json.loads(data)

    server_id = data['sid']
    char_id = data['cid']
    staff_id = data['staff_id']

    tp = TrainingProperty(server_id, char_id)
    tp.callback(staff_id)
    return HttpResponse()


def training_broadcast_callback(request):
    data = request.POST['data']
    data = json.loads(data)

    server_id = data['sid']
    char_id = data['cid']
    slot_id = data['slot_id']

    tb = TrainingBroadcast(server_id, char_id)
    tb.callback(slot_id)
    return HttpResponse()


def training_shop_callback(request):
    data = request.POST['data']
    data = json.loads(data)

    server_id = data['sid']
    char_id = data['cid']
    shop_id = data['shop_id']

    ts = TrainingShop(server_id, char_id)
    ts.callback(shop_id)
    return HttpResponse()


def skill_upgrade_callback(request):
    data = request.POST['data']
    data = json.loads(data)

    server_id = data['sid']
    char_id = data['cid']
    staff_id = data['staff_id']
    skill_id = data['skill_id']

    SkillManager(server_id, char_id).timer_callback(staff_id, skill_id)
    return HttpResponse()


def auction_staff_callback(request):
    data = request.POST['data']
    data = json.loads(data)

    server_id = data['sid']
    char_id = data['cid']
    item_id = data['item_id']

    AuctionManager(server_id, char_id).callback(item_id)
    return HttpResponse()


def challenge_energize_callback(request):
    data = request.POST['data']
    data = json.loads(data)

    server_id = data['sid']
    char_id = data['cid']

    Challenge(server_id, char_id).energize_callback()
    return HttpResponse()
