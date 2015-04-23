
import arrow

from utils.http import ProtobufResponse
from protomsg.server_pb2 import GetServerListResponse, StartGameResponse
from protomsg.common_pb2 import OPT_OK, OPT_CREATE_CHAR, OPT_CREATE_CLUB

from apps.server.models import Server
from apps.character.models import Character
from apps.club.models import Club

def get_server_list(request):
    now = arrow.utcnow().format("YYYY-MM-DD HH:mm:ssZ")

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

    session = request._game_session
    account_id = session.account_id
    server_id = req.server_id

    response = StartGameResponse()
    response.ret = 0

    session.server_id = server_id

    try:
        char = Character.objects.get(account_id=account_id, server_id=server_id)
    except Character.DoesNotExist:
        response.next = OPT_CREATE_CHAR
        response.session = session.serialize()
        return ProtobufResponse(response)

    char_id = char.id
    session.char_id = char_id

    try:
        club = Club.objects.get(char_id=char_id)
    except Club.DoesNotExist:
        response.next = OPT_CREATE_CLUB
        response.session = session.serialize()
        return ProtobufResponse(response)

    session.club_id = club.id

    response.next = OPT_OK
    response.session = session.serialize()
    return ProtobufResponse(response)

