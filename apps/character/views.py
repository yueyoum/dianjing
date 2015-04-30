
from django.db import IntegrityError
from dianjing.exception import GameException
from apps.character.models import Character
from apps.character.core import CharacterManager
from utils.http import ProtobufResponse

from protomsg.character_pb2 import CreateCharacterResponse
from protomsg.common_pb2 import OPT_CREATE_CLUB

from config import CONFIG



CHAR_NAME_MAX_LENGTH = 7

def create(request):
    req = request._proto
    name = req.name

    if not name:
        raise GameException( CONFIG.ERRORMSG["BAD_MESSAGE"].id )
    if len(name) > CHAR_NAME_MAX_LENGTH:
        raise GameException( CONFIG.ERRORMSG["CHAR_NAME_TOO_LONG"].id )

    session = request._game_session

    account_id = session.account_id
    server_id = session.server_id

    try:
        char = Character.objects.create(
            account_id=account_id,
            server_id=server_id,
            name=name,
        )
    except IntegrityError as e:
        if 'account_id' in e.args[1]:
            raise GameException( CONFIG.ERRORMSG["CHAR_ALREAD_CREATED"].id )
        raise GameException( CONFIG.ERRORMSG["CHAR_NAME_TAKEN"].id )

    CharacterManager(char.id).send_notify()

    session.char_id = char.id

    response = CreateCharacterResponse()
    response.ret = 0
    response.next = OPT_CREATE_CLUB
    response.session = session.serialize()

    return ProtobufResponse(response)

