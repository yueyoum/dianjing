
import arrow

from utils.http import ProtobufResponse
from protomsg.server_pb2 import GetServerListResponse, StartGameResponse
from protomsg.common_pb2 import OPT_OK, OPT_CREATE_CHAR, OPT_CREATE_CLUB

from apps.server.models import Server
from apps.character.models import Character
from apps.club.models import Club
from utils.session import GameSession

def get_server_list(request):
    now = arrow.utcnow().format("YYYY-MM-DD HH:mm:ss")

    servers = Server.objects.filter(open_at__gte=now)
    response = GetServerListResponse()
    response.ret = 0
    for server in servers:
        s = response.servers.add()
        s.id = server.id
        s.name = server.name
        s.status = server.status

    # XXX
    response.recent_server_ids.append(1)

    return ProtobufResponse(response)

def start_game(request):
    req = request._proto

    session = GameSession.loads(req.session)
    account_id = session.account_id

    print "account_id"
    print account_id, type(account_id)

    server_id = req.server_id

    response = StartGameResponse()
    response.ret = 0

    session_kwargs = session.kwargs
    session_kwargs['server_id'] = req.server_id

    try:
        char = Character.objects.get(account_id=account_id, server_id=server_id)
    except Character.DoesNotExist:
        response.next = OPT_CREATE_CHAR
        return ProtobufResponse(response)

    char_id = char.id
    session_kwargs['char_id'] = char_id

    try:
        club = Club.objects.get(char_id=char_id)
    except Club.DoesNotExist:
        response.next = OPT_CREATE_CLUB
        session = GameSession.dumps(session_kwargs)
        return ProtobufResponse(response, session=session)

    club_id = club.id
    session_kwargs['club_id'] = club_id

    session = GameSession.dumps(session_kwargs)
    response.next = OPT_OK
    return ProtobufResponse(response, session=session)

