# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       statistics
Date Created:   2016-11-03 10:30
Description:

"""

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render_to_response
from django.db.models import Q, Sum
from django.conf import settings

import arrow
import openpyxl

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
        this_total_purchase = ModelPurchase.objects.filter(server_id=s.id).aggregate(Sum('fee'))['fee__sum']
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



class PurchaseInfo(object):
    HEADERS = ['sid', 'account_id', 'char_id', 'char_name',
               'goods_id', 'fee', 'purchase_at', 'platform']

    HEADER_NAME_TABLE = {
        'sid': '服务器ID',
        'account_id': '账号ID',
        'char_id': '角色ID',
        'char_name': '角色名字',
        'goods_id': '商品ID',
        'fee': '充值金额',
        'purchase_at': '充值时间',
        'platform': '渠道',
    }

    def __init__(self):
        self.headers = [self.HEADER_NAME_TABLE[h] for h in self.HEADERS]
        self.rows = []

    def query(self, sid, date1, date2):
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
            if p.char_id in _char_info_table:
                _char_info_table[p.char_id].append(row)
            else:
                _char_info_table[p.char_id] = [row]

        for c in ModelCharacter.objects.filter(id__in=_char_info_table.keys()):
            for _row in _char_info_table[c.id]:
                _row['account_id'] = c.account_id
                _row['char_name'] = c.name

        for row in info:
            self.add_row(row)

    def add_row(self, data):
        row = [data[h] for h in self.HEADERS]
        self.rows.append(row)

    def to_excel_workbook(self):
        wb = openpyxl.Workbook()
        ws = wb.worksheets[0]
        ws.append(self.headers)
        for row in self.rows:
            ws.append(row)

        return wb


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
        date2 = arrow.get(date2).replace(days=1).format("YYYY-MM-DD HH:mm:ssZ")
    except:
        ret = {
            'ret': 1,
            'msg': '请求数据错误'
        }

        return JsonResponse(ret)

    pi = PurchaseInfo()
    pi.query(sid, date1, date2)

    ret = {
        'ret': 0,
        'header': pi.headers,
        'rows': pi.rows
    }

    return JsonResponse(ret)

def purchase_info_download(request):
    try:
        sid = int(request.GET['sid'])
        date1 = request.GET['date1']
        date2 = request.GET['date2']

        date1 = arrow.get(date1).format("YYYY-MM-DD HH:mm:ssZ")
        date2 = arrow.get(date2).replace(days=1).format("YYYY-MM-DD HH:mm:ssZ")
    except:
        ret = {
            'ret': 1,
            'msg': '请求数据错误'
        }

        return JsonResponse(ret)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=purchase.xlsx'

    pi = PurchaseInfo()
    pi.query(sid, date1, date2)

    wb = pi.to_excel_workbook()
    wb.save(response)
    return response

def retained_info(request):
    return render_to_response('dianjing_statistics_retained.html')
