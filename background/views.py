from django.shortcuts import render_to_response, HttpResponse
from django.http import Http404

from .models import get_servers, DBHandle

from json import JSONEncoder

from apps.character.models import Character
# Create your views here.


def data(request):
    try:
        text = request.GET['text']
    except:
        return render_to_response("search_sql.html")

    try:
        dataObj = Character.objects.filter(name__icontains=text)
    except:
        return HttpResponse('null')

    get_data = []
    for c in dataObj:
        tmp_data = {}
        if c.account_id:
            tmp_data['id'] = c.id
        else:
            tmp_data['id'] = 'null'

        if c.account_id:
            tmp_data['account_id'] = c.account_id
        else:
            tmp_data['account_id'] = 'null'

        if c.name:
            tmp_data['name'] = c.name
        else:
            tmp_data['name'] = 'null'

        if c.server_id:
            tmp_data['server_id'] = c.server_id
        else:
            tmp_data['server_id'] = 'null'

        if c.create_at:
            print c.create_at
            tmp_data['create_at'] = c.create_at.strftime('%Y-%m-%d %H:%M:%S')
        else:
            tmp_data['create_at'] = 'null'

        if c.club_name:
            tmp_data['club_name'] = c.club_name
        else:
            tmp_data['club_name'] = 'null'

        get_data.append(tmp_data)

    tmp = JSONEncoder().encode(get_data)
    return HttpResponse(tmp)


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


def search(request):
    try:
        server_id = request.GET['server_id']
        tp = request.GET['type']
        text = request.GET['text']
    except:
        raise Http404("Error URL")

    one_data = DBHandle(int(server_id)).get_char(tp, text)
    tmp = JSONEncoder().encode(one_data)
    print tmp
    return render_to_response("data_index.html",
                              {'html': 'char.html',
                               'server_id': server_id,
                               'data': tmp,
                               'web_title': 'Data'})


def mails(request):
    server_id = request.GET['server_id']
    char_id = request.GET['char_id']
    mail = DBHandle(int(server_id)).get_mail(int(char_id))
    tmp = JSONEncoder().encode(mail)
    print tmp
    return render_to_response("data_index.html",
                              {'html': 'mail_index.html',
                               'server_id': server_id,
                               'data': tmp,
                               'web_title': 'Mail'})


def mail_one(request):
    server_id = request.GET['server_id']
    char_id = request.GET['char_id']
    mail_id = request.GET['mail_id']

    mail = DBHandle(int(server_id)).get_one_mail(int(char_id), mail_id)

    tmp = JSONEncoder().encode(mail)
    print tmp
    return render_to_response("data_index.html",
                              {'html': 'mail.html',
                               'server_id': server_id,
                               'data': tmp,
                               'web_title': 'Mail'})


def staff(request):
    server_id = request.GET['server_id']
    char_id = request.GET['char_id']

    friends = DBHandle(int(server_id)).get_staff(int(char_id))
    tmp = JSONEncoder().encode(friends)
    print tmp
    return render_to_response("data_index.html",
                              {'html': 'staff.html',
                               'server_id': server_id,
                               'data': tmp,
                               'web_title': 'Staff'})


def friend(request):
    server_id = request.GET['server_id']
    char_id = request.GET['char_id']

    friends = DBHandle(int(server_id)).get_friend(int(char_id))
    tmp = JSONEncoder().encode(friends)
    print tmp
    return render_to_response("data_index.html",
                              {'html': 'friend.html',
                               'server_id': server_id,
                               'data': tmp,
                               'web_title': 'Mail'})


def knapsack(request):
    server_id = request.GET['server_id']
    char_id = request.GET['char_id']

    friends = DBHandle(int(server_id)).get_knapsack(int(char_id))
    tmp = JSONEncoder().encode(friends)
    print tmp
    return render_to_response("data_index.html",
                              {'html': 'knapsack.html',
                               'server_id': server_id,
                               'data': tmp,
                               'web_title': 'Staff'})

def ladder(request):
    server_id = request.GET['server_id']

    return render_to_response("data_index.html",
                              {'html': 'ladder.html',
                               'server_id': server_id,
                               'data': tmp,
                               'web_title': 'Staff'})
