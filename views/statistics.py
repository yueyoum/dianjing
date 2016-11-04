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

from core.mongo import MongoCharacterLoginLog
from utils.functional import get_start_time_of_today

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

        date1 = arrow.get(date1).replace(tzinfo=settings.TIME_ZONE)
        date2 = arrow.get(date2).replace(tzinfo=settings.TIME_ZONE).replace(days=1)
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

        date1 = arrow.get(date1).replace(tzinfo=settings.TIME_ZONE)
        date2 = arrow.get(date2).replace(tzinfo=settings.TIME_ZONE).replace(days=1)
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
    if request.method == 'GET':
        servers_select = []
        for s in ModelServer.opened_servers():
            servers_select.append({'display': s.id, 'value': s.id})

        context = {
            'current': 'retained',
            'servers_select': servers_select,
        }

        return render_to_response(
            'dianjing_statistics_retained.html',
            context=context
        )

    try:
        sid = int(request.POST['sid'])
        date1 = request.POST['date1']
        date2 = request.POST['date2']

        date1 = arrow.get(date1).replace(tzinfo=settings.TIME_ZONE)
        date2 = arrow.get(date2).replace(tzinfo=settings.TIME_ZONE).replace(days=1)
    except:
        ret = {
            'ret': 1,
            'msg': '请求数据错误'
        }

        return JsonResponse(ret)

    pi = RetainedInfo()
    pi.query(sid, date1, date2)

    ret = {
        'ret': 0,
        'header': pi.headers,
        'rows': pi.rows
    }

    return JsonResponse(ret)


def retained_info_download(request):
    try:
        sid = int(request.GET['sid'])
        date1 = request.GET['date1']
        date2 = request.GET['date2']

        date1 = arrow.get(date1).replace(tzinfo=settings.TIME_ZONE)
        date2 = arrow.get(date2).replace(tzinfo=settings.TIME_ZONE).replace(days=1)
    except:
        ret = {
            'ret': 1,
            'msg': '请求数据错误'
        }

        return JsonResponse(ret)

    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=retained.xlsx'

    pi = RetainedInfo()
    pi.query(sid, date1, date2)

    wb = pi.to_excel_workbook()
    wb.save(response)
    return response



###########################

DATE_FORMAT = "YYYY-MM-DD HH:mm:ssZ"


class BaseInfo(object):
    HEADERS = []
    HEADER_NAME_TABLE = {}

    def __init__(self):
        self.headers = [self.HEADER_NAME_TABLE[h] for h in self.HEADERS]
        self.rows = []

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


class PurchaseInfo(BaseInfo):
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

    def query(self, sid, date1, date2):
        """

        :type sid: int
        :type date1: arrow.Arrow
        :type date2: arrow.Arrow
        """
        info = []
        condition = Q(create_at__gte=date1.format(DATE_FORMAT)) & Q(create_at__lte=date2.format(DATE_FORMAT))
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


class RetainedInfo(BaseInfo):
    HEADERS = ['sid', 'date', 'char_increase', 'total_char_increase',
               'retained_1day', 'retained_3day', 'retained_7day', 'retained_15day',
               'purchase_char_amount',
               'purchase_fee']

    HEADER_NAME_TABLE = {
        'sid': '服务器ID',
        'date': '日期',
        'char_increase': '新增用户数',
        'total_char_increase': '总新增用户',
        'retained_1day': '次日留存',
        'retained_3day': '3日留存',
        'retained_7day': '7日留存',
        'retained_15day': '15次日留存',
        'purchase_char_amount': '充值人数',
        'purchase_fee': '总充值金额',
    }

    def query(self, sid, date1, date2):
        """

        :type sid: int
        :type date1: arrow.Arrow
        :type date2: arrow.Arrow
        """
        dates = []
        char_create_info = {}
        purchase_create_info = {}
        purchase_fee_info = {}

        start = date1
        while start < date2:
            date_text = start.format("YYYY-MM-DD")
            dates.append(date_text)
            char_create_info[date_text] = []
            purchase_create_info[date_text] = set()
            purchase_fee_info[date_text] = 0

            start = start.replace(days=1)

        condition = Q(server_id=sid) & Q(create_at__lt=date1.format(DATE_FORMAT))
        char_create_amount_before_date1 = ModelCharacter.objects.filter(condition).count()

        condition = Q(server_id=sid) & Q(create_at__lt=date1.format(DATE_FORMAT))
        purchase_fee_before_date1 = ModelPurchase.objects.filter(condition).aggregate(Sum('fee'))['fee__sum']
        if not purchase_fee_before_date1:
            purchase_fee_before_date1 = 0

        # create
        condition = Q(server_id=sid) & Q(create_at__gte=date1.format(DATE_FORMAT)) & \
                    Q(create_at__lte=date2.format(DATE_FORMAT))
        model_chars = ModelCharacter.objects.filter(condition).order_by('create_at')
        for c in model_chars:
            create_at = arrow.get(c.create_at).to(settings.TIME_ZONE).format("YYYY-MM-DD")
            char_create_info[create_at].append(c.id)

        # purchase
        condition = Q(server_id=sid) & Q(create_at__gte=date1.format(DATE_FORMAT)) & \
                    Q(create_at__lte=date2.format(DATE_FORMAT))
        model_purchase = ModelPurchase.objects.filter(condition).order_by('create_at')
        for p in model_purchase:
            create_at = arrow.get(p.create_at).to(settings.TIME_ZONE).format("YYYY-MM-DD")
            purchase_create_info[create_at].add(p.char_id)
            purchase_fee_info[create_at] += p.fee

        rows = []
        for d in dates:
            row = {
                'sid': 1,
                'date': d,
                'char_increase': len(char_create_info[d]),
                'retained_1day': self.get_retained_for_date(sid, char_create_info[d], d, 1),
                'retained_3day': self.get_retained_for_date(sid, char_create_info[d], d, 3),
                'retained_7day': self.get_retained_for_date(sid, char_create_info[d], d, 7),
                'retained_15day': self.get_retained_for_date(sid, char_create_info[d], d, 15),

                'purchase_char_amount': len(purchase_create_info[d]),
                'purchase_fee': purchase_fee_info[d],
            }

            rows.append(row)

        rows[0]['total_char_increase'] = char_create_amount_before_date1 + rows[0]['char_increase']
        rows[0]['purchase_fee'] = purchase_fee_before_date1 + rows[0]['purchase_fee']

        for i in range(1, len(rows)):
            rows[i]['total_char_increase'] = rows[i - 1]['total_char_increase'] + rows[i]['char_increase']
            rows[i]['purchase_fee'] = rows[i - 1]['purchase_fee'] + rows[i]['purchase_fee']

        for row in rows:
            self.add_row(row)

    def get_login_amount_for_date(self, sid, date, char_ids):
        start = date
        end = date.replace(days=1)

        condition = {'$and': [
            {'char_id': {'$in': char_ids}},
            {'timestamp': {'$gte': start.timestamp}},
            {'timestamp': {'$lte': end.timestamp}}
        ]}

        docs = MongoCharacterLoginLog.db(sid).find(condition)

        char_ids = set()
        for doc in docs:
            char_ids.add(doc['char_id'])

        return len(char_ids)

    def get_retained_for_date(self, sid, char_ids, date_text, days):
        # 找这个date的 days留存
        date = arrow.get(date_text).replace(tzinfo=settings.TIME_ZONE).replace(days=days)
        if date > get_start_time_of_today():
            return '?'

        if not char_ids:
            return '0.0%'

        login_amount = self.get_login_amount_for_date(sid, date, char_ids)
        retained = float(login_amount) / len(char_ids)
        value = '%.1f' % (retained * 100) + '%'
        return value
