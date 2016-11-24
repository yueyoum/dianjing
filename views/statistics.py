# -*- coding: utf-8 -*-
"""
Author:         Wang Chao <yueyoum@gmail.com>
Filename:       statistics
Date Created:   2016-11-03 10:30
Description:

"""

from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render_to_response
from django.db.models import Q, Sum
from django.conf import settings

import arrow
import openpyxl

from apps.account.models import Account as ModelAccount
from apps.account.models import AccountRegular as ModelAccountRegular
from apps.character.models import Character as ModelCharacter
from apps.server.models import Server as ModelServer
from apps.purchase.models import Purchase as ModelPurchase
from apps.statistics.models import Statistics as ModelStatistics

from core.mongo import MongoCharacterLoginLog, MongoResource, MongoUnion, MongoUnionMember
from core.club import Club, get_total_property
from core.staff import StaffManger
from core.formation import Formation
from core.bag import Bag
from core.vip import VIP
from core.territory import Territory
from core.union import Union
from core.arena import Arena, ArenaScore, is_npc_club

from utils.functional import get_start_time_of_today

from config import ConfigItemNew


def get_servers_select_context(show_all=False):
    if show_all:
        servers_select = [{'display': '全部', 'value': 0}]
    else:
        servers_select = []

    for s in ModelServer.opened_servers():
        servers_select.append({'display': s.id, 'value': s.id})

    return servers_select


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
        servers_select = get_servers_select_context(show_all=True)
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
        servers_select = get_servers_select_context()
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


def gold_info(request):
    if request.method == 'GET':
        servers_select = get_servers_select_context()
        context = {
            'current': 'gold',
            'servers_select': servers_select,
        }

        return render_to_response(
            'dianjing_statistics_money.html',
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

    total_gold = get_total_property(sid, 'gold')
    extra_content = u"<h3>全服金币数量: {0}</h3>".format(total_gold)

    gi = GoldInfo()
    gi.query(sid, date1, date2)

    ret = {
        'ret': 0,
        'header': gi.headers,
        'rows': gi.rows,
        'extra_content': extra_content,
    }

    return JsonResponse(ret)


def gold_info_download(request):
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
    response['Content-Disposition'] = 'attachment;filename=gold.xlsx'

    gi = GoldInfo()
    gi.query(sid, date1, date2)

    wb = gi.to_excel_workbook()
    wb.save(response)
    return response


def diamond_info(request):
    if request.method == 'GET':
        servers_select = get_servers_select_context()
        context = {
            'current': 'diamond',
            'servers_select': servers_select,
        }

        return render_to_response(
            'dianjing_statistics_money.html',
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

    total_gold = get_total_property(sid, 'diamond')
    extra_content = u"<h3>全服钻石数量: {0}</h3>".format(total_gold)

    di = DiamondInfo()
    di.query(sid, date1, date2)

    ret = {
        'ret': 0,
        'header': di.headers,
        'rows': di.rows,
        'extra_content': extra_content,
    }

    return JsonResponse(ret)


def diamond_info_download(request):
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
    response['Content-Disposition'] = 'attachment;filename=diamond.xlsx'

    di = DiamondInfo()
    di.query(sid, date1, date2)

    wb = di.to_excel_workbook()
    wb.save(response)
    return response


def char_info(request):
    context = {
        'current': 'char',
        'error': '',
        'multi': [],
        'show': False,
    }

    def _fast_response(err=u''):
        context['error'] = err
        return render_to_response(
            'dianjing_statistics_char.html',
            context=context
        )

    def _multi_response(_chars):
        multi = []
        for _c in _chars:
            multi.append({
                'char_id': _c.id,
                'char_name': _c.name,
                'account_id': _c.account_id,
                'server_id': _c.server_id
            })

        context['multi'] = multi
        return render_to_response(
            'dianjing_statistics_char.html',
            context=context
        )

    def _single_response(_char):
        context['show'] = True
        context['char_id'] = _char.id
        context['char_name'] = _char.name
        context['server_id'] = _char.server_id

        _club = Club(_char.server_id, _char.id)
        _bag = Bag(_char.server_id, _char.id)
        _vip = VIP(_char.server_id, _char.id)
        _sm = StaffManger(_char.server_id, _char.id)
        _fm = Formation(_char.server_id, _char.id)
        _te = Territory(_char.server_id, _char.id)
        _union = Union(_char.server_id, _char.id)

        context['last_login'] = arrow.get(_club.last_login).to(settings.TIME_ZONE).format("YYYY-MM-DD HH:mm:ss")
        context['club_level'] = _club.level
        context['vip_level'] = _vip.doc['vip']
        context['vip_exp'] = _vip.doc['exp']
        context['power'] = _club.power

        context['diamond'] = _club.diamond
        context['gold'] = _club.gold
        context['crystal'] = _club.crystal
        context['gas'] = _club.gas
        context['item_30007'] = _bag.get_amount_by_item_id(30007)
        context['item_30008'] = _bag.get_amount_by_item_id(30008)
        context['item_30009'] = _bag.get_amount_by_item_id(30009)
        context['item_30015'] = _te.get_work_card_amount()

        _res = MongoResource.db(_char.server_id).find_one({'_id': _char.id})
        if not _res:
            _res = {'resource': {}}
        context['item_30022'] = _res['resource'].get('30022', 0)
        context['item_30023'] = _res['resource'].get('30023', 0)
        context['item_30019'] = _res['resource'].get('30019', 0)

        _union_id = _union.get_joined_union_id()
        if not _union_id:
            context['union'] = {}
        else:
            context['union'] = {
                'id': _union_id,
                'name': _union.union_doc['name'],
                'joined_at': arrow.get(_union.member_doc['joined_at']).to(settings.TIME_ZONE).format(
                    "YYYY-MM-DD HH:mm:ss"),
                'contribution': _union.member_doc['contribution']
            }

        in_formation_staffs = _fm.in_formation_staffs()
        staffs_data = []
        equip_data = []

        for k, v in in_formation_staffs.iteritems():
            staff_obj = _sm.get_staff_object(k)
            staff_name = ConfigItemNew.get(staff_obj.oid).name

            staffs_data.append({
                'id': staff_obj.id,
                'oid': staff_obj.oid,
                'name': staff_name,
                'level': staff_obj.level,
                'step': staff_obj.step,
                'star': staff_obj.star,
                'power': staff_obj.power,
                'unit_id': v['unit_id'],
                'position': v['position'],
            })

            for bag_slot_id in [staff_obj.equip_special, staff_obj.equip_decoration, staff_obj.equip_keyboard,
                                staff_obj.equip_monitor, staff_obj.equip_mouse]:

                if not bag_slot_id:
                    continue

                equip = _bag.get_slot(bag_slot_id)
                equip_data.append({
                    'oid': equip['item_id'],
                    'level': equip['level'],
                    'name': ConfigItemNew.get(equip['item_id']).name,
                    'staff_name': staff_name
                })

        context['staffs'] = staffs_data
        context['equips'] = equip_data

        return render_to_response(
            'dianjing_statistics_char.html',
            context=context
        )

    value = request.GET.get('value', '')
    if not value:
        return _fast_response()

    tp = request.GET.get('tp', 3)
    try:
        tp = int(tp)
        assert tp in [1, 2, 3]
        if tp == 3:
            value = int(value)
    except:
        return _fast_response(u"请求数据错误")

    if tp == 1:
        # 账号名
        accounts = ModelAccountRegular.objects.filter(name__icontains=value)
        count = accounts.count()
        if count == 0:
            return _fast_response(u"查询无结果")

        if count > 1:
            account_ids = [a.account.id for a in accounts]
            chars = ModelCharacter.objects.filter(account_id__in=account_ids)
            return _multi_response(chars)

        acc_id = accounts.first().account.id
        char = ModelCharacter.objects.filter(account_id=acc_id)
        return _single_response(char)

    if tp == 2:
        # 角色名
        chars = ModelCharacter.objects.filter(name__icontains=value)
        count = chars.count()
        if count == 0:
            return _fast_response(u"查询无结果")

        if count > 1:
            return _multi_response(chars)

        return _single_response(chars.first())

    # 角色ID
    try:
        char = ModelCharacter.objects.get(id=value)
    except ModelCharacter.DoesNotExist:
        return _fast_response(u"查询无结果")

    return _single_response(char)


def union_info(request):
    servers_select = get_servers_select_context()

    context = {
        'current': 'union',
        'servers_select': servers_select,
        'unions': [],
        'members': [],
    }

    sid = request.GET.get('sid', 0)
    if not sid:
        return render_to_response(
            'dianjing_statistics_union.html',
            context=context
        )

    try:
        sid = int(sid)
    except:
        raise Http404()

    context['sid'] = sid

    uid = request.GET.get('uid', '')
    if not uid:
        docs = MongoUnion.db(sid).find({}).sort('create_at', -1)

        for doc in docs:
            union_data = {
                'id': doc['_id'],
                'name': doc['name'],
                'bulletin': doc['bulletin'],
                'create_at': arrow.get(doc['create_at']).to(settings.TIME_ZONE).format("YYYY-MM-DD HH:mm:ss"),
                'owner': doc['owner'],
                'level': doc['level'],
                'contribution': doc['contribution'],
                'members_amount': MongoUnionMember.db(sid).find({'joined': doc['_id']}).count(),
            }

            context['unions'].append(union_data)

        return render_to_response(
            'dianjing_statistics_union.html',
            context=context
        )

    doc = MongoUnion.db(sid).find_one({'_id': uid})
    if not doc:
        raise Http404()

    context['unions'] = [{
        'id': doc['_id'],
        'name': doc['name'],
        'bulletin': doc['bulletin'],
        'create_at': arrow.get(doc['create_at']).to(settings.TIME_ZONE).format("YYYY-MM-DD HH:mm:ss"),
        'owner': doc['owner'],
        'level': doc['level'],
        'contribution': doc['contribution'],
        'members_amount': MongoUnionMember.db(sid).find({'joined': doc['_id']}).count(),
    }]

    docs = MongoUnionMember.db(sid).find({'joined': uid})
    for doc in docs:
        member_data = {
            'id': doc['_id'],
            'joined_at': arrow.get(doc['joined_at']).to(settings.TIME_ZONE).format("YYYY-MM-DD HH:mm:ss"),
            'contribution': doc['contribution'],
        }

        context['members'].append(member_data)

    return render_to_response(
        'dianjing_statistics_union.html',
        context=context
    )


def arena_info(request):
    servers_select = get_servers_select_context()
    context = {
        'current': 'arena',
        'servers_select': servers_select,
        'clubs': []
    }

    sid = request.GET.get('sid', 0)
    if not sid:
        return render_to_response(
            'dianjing_statistics_arena.html',
            context=context
        )

    try:
        sid = int(sid)
    except:
        raise Http404()

    clubs = Arena.get_leader_board(sid)
    data = []
    for _index, c in enumerate(clubs):
        data.append({
            'rank': _index + 1,
            'id': c.id,
            'name': c.name,
            'level': c.level,
            'power': c.power,
            'score': ArenaScore(sid, c.id).score,
            'is_npc': is_npc_club(str(c.id)),
        })

    context['clubs'] = data
    return render_to_response(
        'dianjing_statistics_arena.html',
        context=context
    )


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
        'sid': '服',
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
        'sid': '服',
        'date': '日期',
        'char_increase': '新增用户数',
        'total_char_increase': '总新增用户',
        'retained_1day': '次日留存',
        'retained_3day': '3日留存',
        'retained_7day': '7日留存',
        'retained_15day': '15日留存',
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


class GoldInfo(BaseInfo):
    HEADERS = [
        'sid', 'date', 'spawn', 'cost', 'cost_by_staff_recruit',
        'cost_by_equip_level_up', 'cost_by_unit_level_up'
    ]

    HEADER_NAME_TABLE = {
        'sid': '服',
        'date': '日期',
        'spawn': '产生',
        'cost': '消耗',
        'cost_by_staff_recruit': '抽卡',
        'cost_by_equip_level_up': '装备升级',
        'cost_by_unit_level_up': '兵种升级',
    }

    def make_empty_data(self, sid, date):
        return {
            'sid': sid,
            'date': date,
            'spawn': 0,
            'cost': 0,
            'cost_by_staff_recruit': 0,
            'cost_by_equip_level_up': 0,
            'cost_by_unit_level_up': 0,
        }

    def query(self, sid, date1, date2):
        """

        :type sid: int
        :type date1: arrow.Arrow
        :type date2: arrow.Arrow
        """

        def make_data(_s, date_str):
            _data = self.make_empty_data(sid, date_str)

            if _s.club_gold == 0:
                return _data

            if _s.club_gold > 0:
                _data['spawn'] = _s.club_gold
                return _data

            _data['cost'] = _s.club_gold
            if _s.message.startswith('StaffRecruit.recruit'):
                _data['cost_by_staff_recruit'] = _s.club_gold
            elif _s.message.startswith('Bag.equipment_level_up'):
                _data['cost_by_equip_level_up'] = _s.club_gold
            elif _s.message.startswith('Unit.level_up'):
                _data['cost_by_unit_level_up'] = _s.club_gold

            return _data

        dates_list = []
        dates = {}
        start = date1
        while start < date2:
            date_str = start.format("YYYY-MM-DD")
            dates[date_str] = self.make_empty_data(sid, date_str)
            dates_list.append(date_str)
            start = start.replace(days=1)

        condition = Q(server_id=sid) & Q(create_at__gte=date1.format(DATE_FORMAT)) & \
                    Q(create_at__lte=date2.format(DATE_FORMAT))

        statistics = ModelStatistics.objects.filter(condition).order_by('create_at')
        for s in statistics:
            create_at_str = arrow.get(s.create_at).to(settings.TIME_ZONE).format("YYYY-MM-DD")
            data = make_data(s, create_at_str)

            dates[create_at_str]['spawn'] += data['spawn']
            dates[create_at_str]['cost'] += data['cost']
            dates[create_at_str]['cost_by_staff_recruit'] += data['cost_by_staff_recruit']
            dates[create_at_str]['cost_by_equip_level_up'] += data['cost_by_equip_level_up']
            dates[create_at_str]['cost_by_unit_level_up'] += data['cost_by_unit_level_up']

        for k in dates_list:
            self.add_row(dates[k])


class DiamondInfo(BaseInfo):
    HEADERS = [
        'sid', 'date', 'spawn', 'cost', 'cost_by_staff_recruit',
        'cost_by_store_buy', 'cost_by_energy_buy', 'cost_by_dungeon_buy',
        'cost_by_tower_reset', 'cost_by_arena_buy', 'cost_by_plunder_buy',
        'cost_by_union_signin', 'cost_by_party_create',
    ]

    HEADER_NAME_TABLE = {
        'sid': '服',
        'date': '日期',
        'spawn': '产生',
        'cost': '消耗',
        'cost_by_staff_recruit': '抽卡',
        'cost_by_store_buy': '神秘商店',
        'cost_by_energy_buy': '体力购买',
        'cost_by_dungeon_buy': '日常副本购买',
        'cost_by_tower_reset': '挑战塔重置',
        'cost_by_arena_buy': '竞技场购买',
        'cost_by_plunder_buy': '掠夺购买',
        'cost_by_union_signin': '公会签到',
        'cost_by_party_create': '宴会创建',
    }

    def make_empty_data(self, sid, date):
        return {
            'sid': sid,
            'date': date,
            'spawn': 0,
            'cost': 0,
            'cost_by_staff_recruit': 0,
            'cost_by_store_buy': 0,
            'cost_by_energy_buy': 0,
            'cost_by_dungeon_buy': 0,
            'cost_by_tower_reset': 0,
            'cost_by_arena_buy': 0,
            'cost_by_plunder_buy': 0,
            'cost_by_union_signin': 0,
            'cost_by_party_create': 0,
        }

    def query(self, sid, date1, date2):
        """

        :type sid: int
        :type date1: arrow.Arrow
        :type date2: arrow.Arrow
        """

        def make_data(_s, date_str):
            _data = self.make_empty_data(sid, date_str)

            if _s.club_diamond == 0:
                return _data

            if _s.club_diamond > 0:
                _data['spawn'] = _s.club_diamond
                return _data

            _data['cost'] = _s.club_diamond
            if _s.message.startswith('StaffRecruit.recruit'):
                _data['cost_by_staff_recruit'] = _s.club_diamond
            elif _s.message.startswith('Store.buy'):
                _data['cost_by_store_buy'] = _s.club_diamond
            elif _s.message.startswith('Energy.buy'):
                _data['cost_by_energy_buy'] = _s.club_diamond
            elif _s.message.startswith('Dungeon.buy_times'):
                _data['cost_by_dungeon_buy'] = _s.club_diamond
            elif _s.message.startswith('Tower.reset'):
                _data['cost_by_tower_reset'] = _s.club_diamond
            elif _s.message.startswith('Arena.buy_times'):
                _data['cost_by_arena_buy'] = _s.club_diamond
            elif _s.message.startswith('Plunder.buy_plunder_times'):
                _data['cost_by_plunder_buy'] = _s.club_diamond
            elif _s.message.startswith('Union.sign_in'):
                _data['cost_by_union_signin'] = _s.club_diamond
            elif _s.message.startswith('Party.start'):
                _data['cost_by_party_create'] = _s.club_diamond

            return _data

        dates_list = []
        dates = {}
        start = date1
        while start < date2:
            date_str = start.format("YYYY-MM-DD")
            dates[date_str] = self.make_empty_data(sid, date_str)
            dates_list.append(date_str)
            start = start.replace(days=1)

        condition = Q(server_id=sid) & Q(create_at__gte=date1.format(DATE_FORMAT)) & \
                    Q(create_at__lte=date2.format(DATE_FORMAT))

        statistics = ModelStatistics.objects.filter(condition).order_by('create_at')
        for s in statistics:
            create_at_str = arrow.get(s.create_at).to(settings.TIME_ZONE).format("YYYY-MM-DD")

            data = make_data(s, create_at_str)
            dates[create_at_str]['spawn'] += data['spawn']
            dates[create_at_str]['cost'] += data['cost']
            dates[create_at_str]['cost_by_staff_recruit'] += data['cost_by_staff_recruit']
            dates[create_at_str]['cost_by_store_buy'] += data['cost_by_store_buy']
            dates[create_at_str]['cost_by_energy_buy'] += data['cost_by_energy_buy']
            dates[create_at_str]['cost_by_dungeon_buy'] += data['cost_by_dungeon_buy']
            dates[create_at_str]['cost_by_tower_reset'] += data['cost_by_tower_reset']
            dates[create_at_str]['cost_by_arena_buy'] += data['cost_by_arena_buy']
            dates[create_at_str]['cost_by_plunder_buy'] += data['cost_by_plunder_buy']
            dates[create_at_str]['cost_by_union_signin'] += data['cost_by_union_signin']
            dates[create_at_str]['cost_by_party_create'] += data['cost_by_party_create']

        for k in dates_list:
            self.add_row(dates[k])
