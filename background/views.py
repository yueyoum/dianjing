from django.shortcuts import render_to_response
from django.http import Http404

from background.models import get_servers, DBHandle

from json import JSONEncoder

from apps.character.models import Character

import arrow

from dianjing import settings

# Create your views here.


def data(request):
    try:
        text = request.GET['text']
        tp = request.GET['type']
        print tp, text
        if tp == 'name':
            dataObj = Character.objects.filter(name__icontains=text)
        if tp == 'id':
            dataObj = Character.objects.filter(id=text)
        if tp == 'club':
            dataObj = Character.objects.filter(club_name__icontains=text)

        get_data = []
        for c in dataObj:
            tmp_data = {}
            tmp_data['id'] = c.pk
            tmp_data['account_id'] = c.account_id
            tmp_data['name'] = c.name

            tmp_data['server_id'] = c.server_id
            tmp_data['last_login'] = arrow.get(c.last_login).to(settings.TIME_ZONE).format("YYYY-MM-DD HH:mm:ss")
            tmp_data['login_times'] = c.login_times

            if c.create_at:
                tmp_data['create_at'] = arrow.get(c.create_at).to(settings.TIME_ZONE).format("YYYY-MM-DD HH:mm:ss")
            else:
                tmp_data['create_at'] = 'null'

            if c.club_name:
                tmp_data['club_name'] = c.club_name
            else:
                tmp_data['club_name'] = 'null'
            get_data.append(tmp_data)
    except:
        return render_to_response("data_index.html")

    print get_data
    return render_to_response("data_index.html", {'data': get_data})


def servers(request):
    server_list = get_servers()
    data = []
    for s in server_list:
        temp = {}
        temp['id'] = s.id
        temp['name'] = s.name
        temp['status'] = s.status
        temp['open_at'] = s.open_at
        temp['mongo_host'] = s.mongo_host
        temp['mongo_port'] = s.mongo_port
        temp['mongo_db'] = s.mongo_db
        data.append(temp)
    return render_to_response('servers.html', {'servers': data, 'web_title': 'ServerList'})


def char(request):
    try:
        server_id = int(request.GET['server_id'])
        id = int(request.GET['id'])
    except:
        raise Http404("Error URL")

    one_data = DBHandle(server_id).get_char(id)
    tmp = JSONEncoder().encode(one_data)
    return render_to_response("char.html",
                              {'server_id': server_id,
                               'data': tmp,
                               'web_title': 'Data'})


def staff(request):
    try:
        server_id = int(request.GET['server_id'])
        char_id = int(request.GET['char_id'])
    except:
        raise Http404('Error message')

    friends = DBHandle(server_id).get_staff(char_id)
    tmp = JSONEncoder().encode(friends)
    return render_to_response("staff.html",
                              {'server_id': server_id,
                               'data': tmp,
                               'web_title': 'Staff'})


def friend(request):
    try:
        server_id = int(request.GET['server_id'])
        char_id = int(request.GET['char_id'])
    except:
        raise Http404('Error Message.')

    friends = DBHandle(server_id).get_friend(char_id)
    tmp = JSONEncoder().encode(friends)

    return render_to_response("friend.html",
                              {'server_id': server_id,
                               'data': tmp,
                               'web_title': 'Friend'})


def ladder(request):
    try:
        server_id = int(request.GET['server_id'])
        data_ladder = DBHandle(server_id).get_ladder()
    except:
        raise Http404("Error Message.")

    tmp_data = []
    for l in data_ladder:
        tmp_ladder = {}
        if l['club_name']:
            tmp_ladder['club'] = l['club_name']
            tmp_ladder['type'] = 0
        else:
            club = DBHandle(server_id).get_club(int(l['_id']))
            tmp_ladder['club'] = club['club']['name']
            tmp_ladder['type'] = 1

        tmp_ladder['order'] = l['order']
        tmp_ladder['score'] = l['score']

        tmp_data.append(tmp_ladder)

    tmp = JSONEncoder().encode(tmp_data)
    return render_to_response("ladder.html",
                              {'server_id': server_id,
                               'data': tmp,
                               'web_title': 'Staff'})


def cup(request):
    try:
        server_id = int(request.GET['server_id'])
    except:
        raise Http404("Error!")

    cup_data = DBHandle(server_id).get_cup()
    tmp_data = {}
    tmp_club = {}
    for c in cup_data:
        for k in c['levels']['32']:
            club = DBHandle(server_id).get_cup_club(k)
            tmp_club[k] = club['club_name']

        tmp_data['levels'] = c['levels']
        tmp_data['order'] = c['order']
        if 'last_champion' in c:
            tmp_data['last_champion'] = c['last_champion']
        else:
            tmp_data['last_champion'] = ''

    tmp = JSONEncoder().encode(tmp_data)
    clubs = JSONEncoder().encode(tmp_club)

    return render_to_response('cup.html',
                              {'server_id': server_id,
                               'data': tmp,
                               'web_title': 'Cup',
                               'club': clubs})
