# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       statistics
Date Created:   2016-11-03 10:30
Description:

"""

from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.db.models import Q, Sum
from django.conf import settings

import arrow

from apps.account.models import Account as ModelAccount
from apps.character.models import Character as ModelCharacter
from apps.server.models import Server as ModelServer
from apps.purchase.models import Purchase as ModelPurchase


def index(request):
    account_amount = ModelAccount.objects.count()
    char_amount = ModelCharacter.objects.count()
    total_purchase = ModelPurchase.objects.aggregate(Sum('fee'))['fee__sum']
    if not total_purchase:
        total_purchase = 0

    server_info = []
    for s in ModelServer.opened_servers():
        this_total_purchase = ModelCharacter.objects.filter(server_id=s.id).aggregate(Sum('fee'))['fee__sum']
        if not this_total_purchase:
            this_total_purchase = 0

        info = {
            'sid': s.id,
            'server_name': s.name,
            'opened_at': arrow.get(s.open_at).to(settings.TIME_ZONE).format("YYYY-MM-DD HH:mm:ss"),
            'char_amount': ModelCharacter.objects.filter(server_id=s.id).count(),
            'total_purchase': this_total_purchase
        }

        server_info.append(info)

    context = {
        'current': 'index',
        'account_amount': account_amount,
        'char_amount': char_amount,
        'total_purchase': total_purchase,
        'server_info': server_info
    }

    return render_to_response(
        'dianjing_statistics_index.html',
        context=context
    )


def purchase_info(request):
    if request.method == 'GET':
        servers_select = [{'display': '全部', 'value': 0}]
        for s in ModelServer.opened_servers():
            servers_select.append({'display': s.id, 'value': s.id})

        context = {
            'current': 'purchase',
            'servers_select': servers_select,
        }

        return render_to_response(
            'dianjing_statistics_purchase.html',
            context=context
        )

    try:
        sid = int(request.POST['sid'])
        date1 = request.POST['date1']
        date2 = request.POST['date2']

        date1 = arrow.get(date1).format("YYYY-MM-DD HH:mm:ssZ")
        date2 = arrow.get(date2).format("YYYY-MM-DD HH:mm:ssZ")
    except:
        ret = {
            'ret': 1,
            'msg': '请求数据错误'
        }

        return JsonResponse(ret)

    info = []
    condition = Q(create_at__gte=date1) & Q(create_at__lte=date2)
    if sid != 0:
        condition &= Q(server_id=sid)

    _char_info_table = {}

    for p in ModelPurchase.objects.filter(condition).order_by('-create_at'):
        row = {
            'sid': p.server_id,
            'char_id': p.char_id,
            'goods_id': p.goods_id,
            'fee': p.fee,
            'purchase_at': arrow.get(p.create_at).to(settings.TIME_ZONE).format("YYYY-MM-DD HH:mm:ss"),
            'platform': p.platform
        }

        info.append(row)
        _char_info_table[p.char_id] = row

    for c in ModelCharacter.objects.filter(id__in=_char_info_table.keys()):
        _char_info_table[c.id]['account_id'] = c.account_id
        _char_info_table[c.id]['char_name'] = c.name

    ret = {
        'ret': 0,
        'info': info
    }

    return JsonResponse(ret)


def retained_info(request):
    return render_to_response('dianjing_statistics_retained.html')
