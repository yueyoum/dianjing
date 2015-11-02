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

def building_levelup_callback(request):
    data = request.POST['data']
    data = json.loads(data)

    server_id = data['sid']
    char_id = data['cid']
    building_id = data['building_id']

    bm = BuildingManager(server_id, char_id)
    timestamp = bm.levelup_callback(building_id)

    return JsonResponse({'end': timestamp})
