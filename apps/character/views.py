
from django.db import IntegrityError
from dianjing.exception import GameException
from apps.character.models import Character

from utils.http import ProtobufResponse
from utils.session import GameSession

from protomsg.character_pb2 import CreateCharacterResponse
from protomsg.common_pb2 import OPT_CREATE_CLUB


def create(request):
    req = request._proto
    name = req.name

    session = GameSession.loads(req.session)

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
            raise GameException(0, 1)
        raise GameException(0, 2)

    session_kwargs = session.kwargs
    session_kwargs['char_id'] = char.id
    session = GameSession.dumps(session_kwargs)

    response = CreateCharacterResponse()
    response.ret = 0
    response.next = OPT_CREATE_CLUB

    return ProtobufResponse(response, session=session)

