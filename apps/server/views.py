

from dianjing.exception import GameException
from utils.http import ProtobufResponse
from protomsg.server_pb2 import GetServerListResponse, StartGameResponse
from protomsg.common_pb2 import OPT_OK, OPT_CREATE_CHAR, OPT_CREATE_CLUB

from apps.server.models import Server
from apps.character.models import Character
from apps.club.models import Club

from config import CONFIG

from component.signals import game_start_signal


def get_server_list(request):
    servers = Server.opened_servers()
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

    if not Server.objects.filter(id=server_id).exists():
        raise GameException( CONFIG.ERRORMSG["BAD_MESSAGE"].id )

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

    game_start_signal.send(
        sender=None,
        server_id=server_id,
        char_id=char_id,
        club_id=club.id
    )

    session.club_id = club.id

    response.next = OPT_OK
    response.session = session.serialize()
    return ProtobufResponse(response)

