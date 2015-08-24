from django.shortcuts import render_to_response

from .models import get_servers, DBHandle


# Create your views here.


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
    return render_to_response('servers.html', {'servers': data})


def collections(request):
    server_id = request.GET['server_id']
    collection_list = DBHandle(int(server_id)).get_collections()
    return render_to_response('collections.html', {'data': collection_list, 'server_id': server_id})


def building(request):
    server_id = request.GET['server_id']
    buildings = DBHandle(int(server_id)).get_building()
    data = []
    for d in buildings:
        temp = {}
        t = {}
        temp['id'] = d['_id']
        for k, v in d['buildings'].items():
            t[str(k)] = v
        temp['buildings'] = t
        data.append(temp)
    return render_to_response('building.html', {'data': data})


def character(request):
    server_id = request.GET['server_id']
    chars = DBHandle(int(server_id)).get_char()
    data = []
    for c in chars:
        c['id'] = c['_id']
        c['club'] = c['club']['name']
        data.append(c)
    return render_to_response('char.html', {'data': data, 'server_id': server_id})


def club(request):
    servers_id = request.GET['server_id']
    char_id = request.GET['char_id']
    char = DBHandle(int(servers_id)).get_club(int(char_id))
    char['id'] = char['_id']
    return render_to_response('club.html', {'data': char, 'servers_id': servers_id})


def common(request):
    server_id = request.GET['server_id']
    common_data = DBHandle(int(server_id)).get_common()
    data = []
    for d in common_data:
        print d
    return render_to_response('common.html', {'data': data})


def friend(request):
    server_id = request.GET['server_id']
    friend_data = DBHandle(int(server_id)).get_friend()
    data = []
    for d in friend_data:
        friends = {}
        friends['char_id'] = d['_id']
        friends['friends'] = d['friends']
        print friends
        data.append(friends)
    return render_to_response('friend.html', {'data': data})


def league_event(request):
    server_id = request.GET['server_id']
    league_event_data = DBHandle(int(server_id)).get_league_event()
    data = []
    for l in league_event_data:
        l['id'] = l['_id']
        data.append(l)

    return render_to_response('league_event.html', {'data': data})


def league_group(request):
    server_id = request.GET['server_id']
    league_group_data = DBHandle(int(server_id)).get_league_group()
    data = []
    for l in league_group_data:
        l['id'] = l['_id']
        data.append(l)

    return render_to_response('league_group.html', {'data': data})


def mail(request):
    server_id = request.GET['server_id']
    mails = DBHandle(int(server_id)).get_mail()
    data = []
    for d in mails:
        t = {}
        t['id'] = d['_id']
        title = []
        for k, v in d['mails'].items():
            mail_t = {}
            mail_t['key'] = k
            mail_t['title'] = v['title']
            title.append(mail_t)

        t['mails'] = title
        print t
        data.append(t)

    return render_to_response('mail_index.html', {'data': data, 'server_id': server_id})


def mail_one(request):
    server_id = request.GET['server_id']
    mail_id = request.GET['mail_id']
    char_id = request.GET['char_id']
    mails = DBHandle(int(server_id)).get_mail_one(int(char_id), mail_id)

    data = {}
    for k, v in mails['mails'].items():
        if k == mail_id:
            data['char_id'] = char_id
            data['key'] = k
            data['title'] = v['title']
            data['from_id'] = v['from_id']
            data['content'] = v['content']
            data['has_read'] = v['has_read']
            data['create_at'] = v['create_at']
            data['attachment'] = v['attachment']

    print data
    return render_to_response('mail.html', {'data': data})


def staff(request):
    server_id = request.GET['server_id']
    staffs = DBHandle(int(server_id)).get_staff()
    data = []
    for d in staffs:
        temp = {}
        temp['id'] = d['_id']
        staff_list = []
        for st_k, st_v in d['staffs'].items():
            staff_list.append(st_k)
        temp['staffs'] = staff_list
        temp['trainings'] = d['trainings']
        data.append(temp)
    return render_to_response('staff.html', {'data': data, 'server_id': server_id})


def staff_char(request):
    server_id = request.GET['server_id']
    char_id = request.GET['char_id']
    data = DBHandle(int(server_id)).get_char_staff(int(char_id))
    data['id'] = data['_id']
    print data
    return render_to_response('char_staff.html', {'data': data})


def recruit(request):
    server_id = request.GET['server_id']
    recruits = DBHandle(int(server_id)).get_recruit()
    data = []
    for r in recruits:
        r['id'] = r['_id']
        data.append(r)

    print data
    return render_to_response('recruit.html', {'data': data})


def training_store(request):
    server_id = request.GET['server_id']
    trainings = DBHandle(int(server_id)).get_training_store()

    data = []
    for t in trainings:
        t['id'] = t['_id']
        data.append(t)
        print t

    return render_to_response('training_store.html', {'data': data})
