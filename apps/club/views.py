
from django.db import IntegrityError
from dianjing.exception import GameException
from apps.character.models import Character
from apps.club.models import Club

from utils.http import ProtobufResponse
from config import CONFIG

from protomsg.club_pb2 import CreateClubResponse

from component.signals import game_start_signal

def create(request):
    name = request._proto.name
    flag = request._proto.flag

    session = request._game_session
    server_id = session.server_id
    char_id = session.char_id

    if Club.objects.filter(char_id=char_id).exists():
        raise GameException( CONFIG.ERRORMSG["CLUB_ALREADY_CREATED"].id )

    char_name = Character.objects.get(id=char_id).name

    try:
        club = Club.objects.create(
            char_id=char_id,
            char_name=char_name,
            server_id=server_id,
            name=name,
            flag=flag
        )
    except IntegrityError as e:
        raise GameException( CONFIG.ERRORMSG["CLUB_NAME_TAKEN"].id )

    # XXX for develop
    from apps.staff.core import StaffManager
    StaffManager(char_id).add(1, send_notify=False)
    StaffManager(char_id).add(2, send_notify=False)
    # XXX

    game_start_signal.send(
        sender=None,
        server_id=server_id,
        char_id=char_id,
        club_id=club.id,
    )

    session.club_id = club.id

    response = CreateClubResponse()
    response.ret = 0
    response.session = session.serialize()
    return ProtobufResponse(response)
